import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the Haversine distance between two points on the earth.
    """
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def solve_tsp_greedy(points):
    """
    Solves TSP using a greedy nearest-neighbor approach.
    Points is a list of (lat, long) tuples.
    Returns ordered list of points and total distance.
    """
    if not points:
        return [], 0
    
    # Start at the first point (arbitrary depot or current location)
    current_pos = points[0]
    path = [current_pos]
    unvisited = set(points[1:])
    total_dist = 0
    
    while unvisited:
        nearest_point = None
        min_dist = float('inf')
        
        for point in unvisited:
            dist = haversine_distance(current_pos[0], current_pos[1], point[0], point[1])
            if dist < min_dist:
                min_dist = dist
                nearest_point = point
        
        current_pos = nearest_point
        path.append(current_pos)
        unvisited.remove(current_pos)
        total_dist += min_dist
        
    # Return to start? The PDF implies "optimizar rutas", usually round trip or just efficient delivery.
    # Let's assume open path for now or return to start if needed. Let's do open path for simplicity unless "Depot" is specified.
    # Actually, usually fleets return to depot. Let's add return to start distance.
    
    return_dist = haversine_distance(current_pos[0], current_pos[1], path[0][0], path[0][1])
    total_dist += return_dist
    path.append(path[0]) # Close the loop
    
    return path, total_dist

def optimize_routes(df, n_vehicles=5):
    """
    Optimizes routes for the fleet using Clustering + TSP.
    
    Args:
        df (pd.DataFrame): DataFrame with 'lat' and 'long'.
        n_vehicles (int): Number of vehicles/routes to create.
        
    Returns:
        routes (dict): Dictionary of vehicle_id -> ordered path.
    """
    print("\n--- Optimizing Routes ---")
    
    # Filter valid locations
    df_loc = df.dropna(subset=['lat', 'long']).copy()
    
    if len(df_loc) < n_vehicles:
        print("Not enough data points for clustering.")
        return {}
    
    # 1. Clustering (Assign stops to vehicles)
    kmeans = KMeans(n_clusters=n_vehicles, random_state=42, n_init=10)
    df_loc['cluster'] = kmeans.fit_predict(df_loc[['lat', 'long']])
    
    routes = {}
    
    plt.figure(figsize=(10, 6))
    colors = plt.cm.get_cmap('tab10', n_vehicles)
    
    for i in range(n_vehicles):
        cluster_points = df_loc[df_loc['cluster'] == i][['lat', 'long']].values
        points_tuple = [tuple(x) for x in cluster_points]
        
        if not points_tuple:
            continue
            
        # 2. TSP (Order stops within cluster)
        ordered_path, dist = solve_tsp_greedy(points_tuple)
        routes[i] = ordered_path
        
        print(f"Vehicle {i+1}: {len(ordered_path)-1} stops, Est. Distance: {dist:.2f} km")
        
        # Plot
        lats = [p[0] for p in ordered_path]
        longs = [p[1] for p in ordered_path]
        plt.plot(longs, lats, marker='o', linestyle='-', label=f'Vehicle {i+1}', color=colors(i))
        
    plt.title('Optimized Fleet Routes')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.grid(True)
    plt.savefig('route_optimization_map.png')
    print("Route map saved to 'route_optimization_map.png'")
    
    return routes

if __name__ == "__main__":
    # Test run
    import sys
    import os
    from data_loader import load_and_preprocess_data
    
    possible_paths = [
        "../67a6fef440f8a5868a2e023e_DLP Labs_Sample.csv",
        "67a6fef440f8a5868a2e023e_DLP Labs_Sample.csv"
    ]
    
    file_path = None
    for p in possible_paths:
        if os.path.exists(p):
            file_path = p
            break
            
    if file_path:
        df = load_and_preprocess_data(file_path)
        optimize_routes(df)
    else:
        print("CSV file not found for testing.")
