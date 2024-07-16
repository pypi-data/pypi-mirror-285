import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
import scipy
import math

import numpy as np
from geopy.distance import geodesic as GD
from shapely.geometry import box
from shapely.geometry import LineString, Point
import shapely
from collections import defaultdict


import folium
from IPython.display import display, HTML
import random


def convert_to_points(coord_list):
    return [Point(coord) for coord in coord_list]


def process_data(df):
    tqdm.pandas()
    df['geometry'] = df['geometry'].progress_apply(convert_to_points)
    df_points = df.explode('geometry')
    gdf = gpd.GeoDataFrame(df_points, geometry='geometry',crs="EPSG:4326")

    return gdf

class ConvertToToken:
    def __init__(self, df, area, cell_size):
        self.cell_size = cell_size
        self.gdf = process_data(df)
        self.area = area

    def create_grid(self):
      '''
      creates a grid of cell size 'n' over a given area
      returns: the grid and the number of rows

      '''

      xmin, ymin, xmax, ymax = self.area.total_bounds

      height = GD((xmax, ymin), (xmax, ymax)).m
      width = GD((xmin, ymin), (xmax, ymin)).m
    #   print(f"Study Area Size: ")
    #   print(f"Width: {width}m")
    #   print(f"Height: {height}m")
    #   print()

      # how many cells across and down
      grid_cells = []

      n_cells_h = height / self.cell_size
      cell_size_h = (ymax - ymin) / n_cells_h

      n_cells_w = width / self.cell_size
      cell_size_w = (xmax - xmin) / n_cells_w

      for x0 in np.arange(xmin, xmax, cell_size_w):
          n_rows = 0
          for y0 in np.arange(ymin, ymax, cell_size_h):
              # bounds
              x1 = x0 + cell_size_w
              y1 = y0 + cell_size_h
              grid_cells.append(shapely.geometry.box(x0, y0, x1, y1))
              n_rows += 1
              # print('n_rows ', n_rows)

      cell = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs="EPSG:4326")
      print('Number of created cells: ', cell.shape[0])

      return cell, n_rows,  cell.shape[0]

    def assign_ids(self, grid, n_rows):
      '''
      assign each cell an ID (tuple of column and row position)

      :param: grid: the entire grid
      :param: n_rows: the number of rows in the grid
      '''

      total = grid.shape[0]
      n_cols = int(total / n_rows)

      tuple_list = []
      for i in range(n_cols):
          for j in range(n_rows):
              tuple_list.append(tuple((i, j)))
      grid['ID'] = tuple_list

      return grid

    def find_grid_center(self, grid):
      '''
      find the centroid of each cell in the grid
      '''

      grid_center = gpd.GeoDataFrame(columns=["geometry", "ID"], geometry='geometry', crs="EPSG:4326")

      grid_projected = grid.to_crs("EPSG:3857")
      centroids = grid_projected.centroid

      centroids_4326 = centroids.to_crs("EPSG:4326")

      grid_center['geometry'] = list(centroids_4326)
      grid_center["ID"] = grid["ID"]

      return grid_center
    
    def merge_with_polygon(self, grid):
        merged_gdf = gpd.sjoin(self.gdf, grid, how='left', predicate='within')
        merged_gdf.drop(columns=['index_right'], inplace=True)
        
        return merged_gdf
        

    def create_tokens(self):

        grid, n_rows, num_cells = self.create_grid()
        assigned_grid = self.assign_ids(grid, n_rows)

        grid_center = self.find_grid_center(assigned_grid)
        merged_gdf = self.merge_with_polygon(grid)


        agg_funcs = {'geometry': list, 'ID':list}  
        grouped_df = merged_gdf.groupby('trip_id').agg(agg_funcs)

        sentences = grouped_df['ID'].tolist()
        sentences = [[x for i, x in enumerate(lst) if i == 0 or x != lst[i - 1]] for lst in sentences]

        
        return grid_center, grouped_df
    

class NgramGenerator:
    def __init__(self, sentence_gdf):
        self.sentences = sentence_gdf['ID'].values.tolist()


    def find_start_end_points(self):
        sentences = [[x for i, x in enumerate(lst) if i == 0 or x != lst[i - 1]] for lst in self.sentences]
        
        start_end_points = []
        for sentence in sentences:
            if len(sentence) > 3:
                start_end_points.append([tuple((sentence[0], sentence[1])), tuple((sentence[-2], sentence[-1]))])

        return start_end_points
    
    def reverse_sentences(self, sentences):
        reversed_sentences = []
        for sent in sentences:
            reverse = sent[::-1]
            reversed_sentences.append(reverse)

        return reversed_sentences


    def create_ngrams(self):

        start_end_points = self.find_start_end_points()
        sentences_reversed = self.reverse_sentences(self.sentences)
        # corpus = self.sentences + sentences_reversed

        bigrams_reversed = {}
        trigrams_reversed = {}

        for sentence in tqdm(sentences_reversed):
            # for word in sentence:
            #     unigram_counts[word] = unigram_counts.get(word, 0) + 1
            #     self.total_unigrams += 1

            for i in range(len(sentence) - 1):
                bigram = (tuple(sentence[i:i+2]))
                bigrams_reversed[bigram] = bigrams_reversed.get(bigram, 0) + 1

            for i in range(len(sentence) - 2):
                trigram = (tuple(sentence[i:i+3]))
                trigrams_reversed[trigram] = trigrams_reversed.get(trigram, 0) + 1
        
        bigrams_original = {}
        trigrams_original = {}
        for sentence in tqdm(self.sentences):

            for i in range(len(sentence) - 1):
                bigram = (tuple(sentence[i:i+2]))
                bigrams_original[bigram] = bigrams_original.get(bigram, 0) + 1

            for i in range(len(sentence) - 2):
                trigram = (tuple(sentence[i:i+3]))
                trigrams_original[trigram] = trigrams_original.get(trigram, 0) + 1

        print(f"\nNumber of Unique Bigrams: {len(bigrams_original)} \nNumber of Unique Trigrams: {len(trigrams_original)}")

        ngrams = {
            'bigrams_orignal': bigrams_original,
            'bigrams_reversed': bigrams_reversed,
            'trigrams_original': trigrams_original,
            'trigrams_reversed': trigrams_reversed
        }

        return  ngrams, start_end_points
 

def process_trigrams(trigrams):
    trigrams_dict = defaultdict(list)
    for trigram, count in trigrams.items():
        first_two_tokens = trigram[:2]
        third_token = trigram[2]
        trigrams_dict[first_two_tokens].append((third_token, count))
    return trigrams_dict

def process_trigrams_2(trigrams):
  trigram_dict_2 = defaultdict(list)
  for trigram in trigrams.keys():
      trigram_dict_2[(trigram[0]), trigram[-1]].append(trigram[1])

  return trigram_dict_2

class TrajGenerator:
    def __init__(self, ngrams, start_end_points, n, grid):
        self.trigrams = {key: ngrams['trigrams_original'].get(key, 0) + ngrams['trigrams_reversed'].get(key, 0) for key in set(ngrams['trigrams_original']) | set(ngrams['trigrams_reversed'])}

        self.trigram_dict = process_trigrams(self.trigrams)
        self.trigram_dict_original= process_trigrams(ngrams['trigrams_original'])
        self.trigrams_dict_2 = process_trigrams_2(self.trigrams)
        self.start_end_points = start_end_points
        self.grid_center = grid
        self.num_sentences = n
        self.k = 3

    @staticmethod
    def start_path(start, end):
        min_distance = float('inf')
        closest_pair = None

        # Calculate the Euclidean distance between each pair of points (one from each list)
        for point1 in start:
            for point2 in end:
                dist = scipy.spatial.distance.euclidean(point1, point2)
                if dist < min_distance:
                    min_distance = dist
                    closest_pair = (point1, point2)


        path_start = [point for point in start + end if point not in closest_pair]

        path_start.insert(1, closest_pair[0])
        path_start.insert(2, closest_pair[-1])

        return path_start

    @staticmethod
    def calculate_distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


    def find_next_tokens(self, left, right, path_sentence):
        next_tokens_l = dict(self.trigram_dict.get(tuple(left), []))
        next_tokens_r = dict(self.trigram_dict.get(tuple(right), []))

        next_tokens_with_counts_l = {key: value for key, value in next_tokens_l.items() if key not in path_sentence}
        next_tokens_with_counts_r = {key: value for key, value in next_tokens_r.items() if key not in path_sentence}

        sorted_next_tokens_l = sorted(next_tokens_with_counts_l.items(), key=lambda x: x[1], reverse=True)
        sorted_next_tokens_l_top_k = sorted_next_tokens_l[:self.k] if len(sorted_next_tokens_l) >= self.k else sorted_next_tokens_l

        sorted_next_tokens_r = sorted(next_tokens_with_counts_r.items(), key=lambda x: x[1], reverse=True)
        sorted_next_tokens_r_top_k = sorted_next_tokens_r[:self.k] if len(sorted_next_tokens_r) >= self.k else sorted_next_tokens_r

        closest_points = {}

        for point1, _ in sorted_next_tokens_l_top_k:
            for point2, _ in sorted_next_tokens_r_top_k:
                distance = TrajGenerator.calculate_distance(point1, point2)
                closest_points[(point1, point2)] = distance

        closest_points_top3 = dict(sorted(closest_points.items(), key=lambda x: x[1], reverse=False)[:self.k])

        points = list(closest_points_top3.keys())
        return points

    def generate_sentences_using_origin_destination(self):
        full_sentence = False

        random_path = random.choice(self.start_end_points)
        start = random_path[0]
        end = random_path[1]

        num_tries = 0
        while not full_sentence:
            path_start = self.start_path(start, end)
            left = path_start[:2]
            right = path_start[-2:]

            path_sentence = path_start
            for i in range(40):

                points = self.find_next_tokens(left, right, path_sentence)
                try:
                    j = random.randint(0, len(points)-1)
                except:
                    continue

                left = [left[-1], points[j][0]]
                right = [right[-1], points[j][1]]

                path_sentence.insert(i+2, left[-1])
                path_sentence.insert(i+3, right[-1])

                # Check if a trigram that matches the left and righ tokens exists in the trigram corpus. 
                # If one exists, the points are close enough and a full 'sentence' is constructed
                if len (self.trigrams_dict_2[left[-1], right[-1]]) > 1:
                    fills = self.trigrams_dict_2[left[-1], right[-1]]

                    trigram_fills = {}
                    for each in fills:
                        trigram = tuple((left[-1], each, right[-1]))
                        trigram_fills[trigram] = self.trigrams[trigram]

                    trigram_with_highest_count = max(trigram_fills, key=lambda k: trigram_fills[k])

                    path_sentence.insert(i+3, trigram_with_highest_count[1])
                    full_sentence = True
                    break
            
            if full_sentence:
                return path_sentence

            num_tries += 1
            if num_tries == 3:
                return []

            

    def generate_sentences_using_origin(self, length, seed=None):
      text = []
      if seed is not None:
          random.seed(seed)
          current_trigram = random.sample(self.start_end_points, min(len(self.start_end_points), self.num_sentences))[0][0]
      else:
          current_trigram = random.choice(self.start_end_points)[0]
      
      text.extend(current_trigram)

      while len(text) < length:
          # Get the list of next tokens and their counts for the current trigram
          next_tokens_with_counts = self.trigram_dict_original.get(current_trigram, [])
          if not next_tokens_with_counts:
              break  

          # Choose the next token based on its counts
          total_count = sum(count for _, count in next_tokens_with_counts)
          random_value = random.randint(1, total_count) 
          cumulative_count = 0
          next_token = None

          #pick the next token randomly from the possible next tokens
          for token, count in next_tokens_with_counts:
              cumulative_count += count
              if random_value <= cumulative_count:
                  next_token = token
                  break

          # Append the next token to the text
          text.append(next_token)

          # Update the current trigram
          current_trigram = current_trigram[1:] + (next_token,)

      return text


    def convert_sentence_to_traj(self, generated_sentences):
        """
        Converts the generated sentences into coordinate points 
        using the centroid of the cell each point falls into.
        
        """
        token_to_geometry = dict(zip(self.grid_center['ID'], self.grid_center['geometry']))
        all_points = []

        for sentence in tqdm(generated_sentences):
            sentence_geometries = [token_to_geometry[token] for token in sentence if token in token_to_geometry]
            all_points.append(sentence_geometries)

        return all_points


    def generate_trajs_using_origin_destination(self):
        new_generated_sentences = []
        with tqdm(total=self.num_sentences, desc="Generating sentences") as pbar:
            while len(new_generated_sentences) < self.num_sentences:
                path_sentence = self.generate_sentences_using_origin_destination()
                if path_sentence:
                    new_generated_sentences.append(path_sentence)
                    pbar.update(1) 

        new_trajs =  self.convert_sentence_to_traj(new_generated_sentences)

        geom_list = []
        for traj in new_trajs:
            coordinates = []
            for point in traj:
                coordinates.append([point.x, point.y])
            geom_list.append(coordinates)

        df = pd.DataFrame({'geometry':geom_list})
        df['trip_id'] = range(1, len(df) + 1)
        df = df[['trip_id', 'geometry']]

        gdf = pd.DataFrame({'geometry':new_trajs})
        gdf['trip_id'] = range(1, len(gdf) + 1)
        gdf = gdf[['trip_id', 'geometry']]

        return df, gdf

    def generate_trajs_using_origin(self, sentence_length, seed=None):
        new_generated_sentences = []

        if seed is not None:
          random.seed(seed)
          random_seeds = [random.randint(1, len(self.start_end_points)) for _ in range(self.num_sentences)]

          with tqdm(total=self.num_sentences, desc="Generating sentences") as pbar:

              # while len(new_generated_sentences) < self.num_sentences:
              for seed in random_seeds:
                  generated_text = self.generate_sentences_using_origin(sentence_length, seed)
                  if len(generated_text) > (sentence_length-5):
                      new_generated_sentences.append(generated_text)
                      pbar.update(1)  # Update the progress bar
          
        else:
          with tqdm(total=self.num_sentences, desc="Generating sentences") as pbar:
              while len(new_generated_sentences) < self.num_sentences:
                  generated_text = self.generate_sentences_using_origin(sentence_length, seed)
                  if len(generated_text) > (sentence_length-5):
                      new_generated_sentences.append(generated_text)
                      pbar.update(1)  # Update the progress bar

        new_trajs =  self.convert_sentence_to_traj(new_generated_sentences)


        geom_list = []
        for traj in new_trajs:
            coordinates = []
            for point in traj:
                coordinates.append([point.x, point.y])
            geom_list.append(coordinates)

        df = pd.DataFrame({'geometry':geom_list})
        df['trip_id'] = range(1, len(df) + 1)
        df = df[['trip_id', 'geometry']]

        gdf = pd.DataFrame({'geometry':new_trajs})
        gdf['trip_id'] = range(1, len(gdf) + 1)
        gdf = gdf[['trip_id', 'geometry']]

        return df, gdf


class DisplayTrajs():
    def __init__(self, original_trajs, generated_trajs):
        self.original_trajs = original_trajs
        self.generated_trajs =  generated_trajs


    def plot_map(self, trajs):

        center_coords = (trajs[0][0].y, trajs[0][0].x)
        mymap = folium.Map(location=center_coords, zoom_start=12)

        for points in trajs:
            line = LineString(points)
            line_coords = [(point[1], point[0]) for point in line.coords]
            folium.PolyLine(locations=line_coords, color='blue').add_to(mymap)

        return mymap


    def display_maps(self):
        map1 = self.plot_map(self.original_trajs)
        map2 = self.plot_map(self.generated_trajs)

        html_map1 = map1._repr_html_()
        html_map2 = map2._repr_html_()

        html = f"""
        <div style="display: flex; justify-content: space-around;">
            <div style="width: 45%;">
                <h3 style="text-align: center;">Original Trajectories</h3>
                {html_map1}
            </div>
            <div style="width: 45%;">
                <h3 style="text-align: center;">Generated Trajectories</h3>
                {html_map2}
            </div>
        </div>
        """

        # Display the HTML
        display(HTML(html))


    def merge_grid_with_points(self, grid, df, num_cells):


        grid['Region'] = [i for i in range(0, num_cells)]
        df = df.explode('geometry')

        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs = "EPSG:4326")
        merged_df = gpd.sjoin(gdf, grid, how='left', predicate='within', lsuffix='_points', rsuffix='_grid')

        region_geometries = {i: grid.loc[i]['geometry'] for i in range(num_cells)}
        polygon_region = []

        for idx, row in tqdm(merged_df.iterrows(), total=len(merged_df)):
            region = row['Region']
            if region in region_geometries:
                polygon_region.append(region_geometries[region])
            else:
                polygon_region.append('nan')

        merged_df['point_region'] = polygon_region

        return merged_df

    def plot_heat_map(self, df, area, ax, cell_size):
        TokenCreator = ConvertToToken(df, area, cell_size)
        grid, n_rows, num_cells = TokenCreator.create_grid()
        df = self.merge_grid_with_points(grid, df, num_cells)

        df_valid = df[df['point_region'] != 'nan']
        polygon_counts = df_valid['point_region'].value_counts()

        polygon_counts_df = pd.DataFrame({'geometry': polygon_counts.index, 'count': polygon_counts.values})
        polygon_counts_gdf = gpd.GeoDataFrame(polygon_counts_df)
        polygon_counts_gdf = polygon_counts_gdf.set_geometry('geometry')

        # Plotting the heatmap
        # fig, ax = plt.subplots(figsize=(10, 6))
        polygon_counts_gdf.plot(column='count', cmap='YlOrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
        area.plot(ax=ax, color = 'none')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('Generated Trajectories')