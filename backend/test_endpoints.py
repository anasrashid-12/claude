import requests
import json
import time
import statistics

BASE_URL = "http://localhost:8000"

def test_health():
    print("\nTesting health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_product():
    print("\nTesting create product endpoint...")
    product_data = {
        "name": "Test Product",
        "price": 29.99,
        "description": "A test product created by the test script"
    }
    
    response = requests.post(
        f"{BASE_URL}/products/",
        json=product_data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get('id')  # Return product ID for next test

def measure_request_time(product_id):
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    end_time = time.time()
    return end_time - start_time, response

def test_get_product(product_id):
    print(f"\nTesting get product endpoint for ID: {product_id}")
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test Redis caching with multiple requests
    print("\nTesting Redis caching...")
    
    # Clear any existing cache by waiting
    print("Waiting for cache to expire...")
    time.sleep(2)
    
    # Make multiple requests to get average times
    num_requests = 20  # Increased from 5 to 20
    print(f"\nMaking {num_requests} requests without cache...")
    uncached_times = []
    
    # Warm-up requests
    print("Performing warm-up requests...")
    for _ in range(3):
        measure_request_time(product_id)
        time.sleep(0.5)
    
    # Actual uncached requests
    for i in range(num_requests):
        time.sleep(0.5)  # Reduced wait time between requests
        request_time, _ = measure_request_time(product_id)
        uncached_times.append(request_time)
        print(f"Request {i+1}: {request_time:.4f} seconds")
    
    # Ensure data is cached
    requests.get(f"{BASE_URL}/products/{product_id}")
    time.sleep(1)  # Short wait to ensure cache is ready
    
    print(f"\nMaking {num_requests} requests with cache...")
    cached_times = []
    for i in range(num_requests):
        request_time, _ = measure_request_time(product_id)
        cached_times.append(request_time)
        print(f"Request {i+1}: {request_time:.4f} seconds")
    
    # Remove outliers (top and bottom 10%)
    def remove_outliers(times):
        sorted_times = sorted(times)
        cut = len(times) // 10
        return sorted_times[cut:-cut] if cut > 0 else sorted_times
    
    uncached_times = remove_outliers(uncached_times)
    cached_times = remove_outliers(cached_times)
    
    # Calculate statistics
    avg_uncached = statistics.mean(uncached_times)
    avg_cached = statistics.mean(cached_times)
    
    print(f"\nAverage uncached request time: {avg_uncached:.4f} seconds")
    print(f"Average cached request time: {avg_cached:.4f} seconds")
    print(f"Cache performance improvement: {((avg_uncached - avg_cached) / avg_uncached * 100):.1f}%")
    
    # Additional statistics
    print(f"\nUncached requests (outliers removed):")
    print(f"  Min: {min(uncached_times):.4f} seconds")
    print(f"  Max: {max(uncached_times):.4f} seconds")
    print(f"  Standard deviation: {statistics.stdev(uncached_times):.4f} seconds")
    
    print(f"\nCached requests (outliers removed):")
    print(f"  Min: {min(cached_times):.4f} seconds")
    print(f"  Max: {max(cached_times):.4f} seconds")
    print(f"  Standard deviation: {statistics.stdev(cached_times):.4f} seconds")

if __name__ == "__main__":
    print("Starting API endpoint tests...")
    
    # Test health endpoint
    test_health()
    
    # Test create product
    product_id = test_create_product()
    
    if product_id:
        # Test get product and caching
        test_get_product(product_id)
    else:
        print("Failed to create product, skipping get product test") 