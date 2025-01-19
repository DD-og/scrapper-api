import requests
import json
from typing import Dict, List, Union
import time
import random
import feedparser
from datetime import datetime, timedelta
import urllib.parse
from bs4 import BeautifulSoup

class ContentFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.delay_range = (1, 2)
        self.news_api_key = '6829434b7662434e992ed2d0613b8d9d'  # NewsAPI key

    def _delay(self):
        """Add random delay between requests"""
        time.sleep(random.uniform(*self.delay_range))

    def extract_industry_terms(self, media_insights: Dict) -> Dict[str, List[str]]:
        """
        Extract industry and product terms from media insights
        """
        text = f"{media_insights.get('marketPosition', '')} {media_insights.get('primaryAudienceDemographics', '')}"
        text = text.lower()
        
        # Define industry patterns to check
        industries = {
            'audio': ['audio', 'music', 'speaker', 'headphone', 'earbud', 'sound'],
            'wearables': ['wearable', 'smartwatch', 'fitness band', 'smart band', 'watch'],
            'mobile': ['smartphone', 'mobile', 'phone', 'tablet'],
            'gaming': ['gaming', 'game', 'console', 'controller'],
            'electronics': ['electronics', 'gadget', 'device', 'appliance'],
            'fashion': ['fashion', 'clothing', 'apparel', 'wear', 'outfit'],
            'beauty': ['beauty', 'cosmetic', 'makeup', 'skincare'],
            'food': ['food', 'beverage', 'drink', 'snack', 'meal'],
            'automotive': ['car', 'vehicle', 'automotive', 'bike', 'scooter'],
            'software': ['software', 'app', 'application', 'digital', 'platform']
        }
        
        # Detect industries mentioned in the text
        detected_industries = []
        for industry, terms in industries.items():
            if any(term in text for term in terms):
                detected_industries.append(industry)
        
        # If no specific industry detected, use 'product' as generic term
        if not detected_industries:
            detected_industries = ['product']
        
        # Extract product types and features from market position
        product_terms = []
        for word in text.split():
            if word not in ['the', 'and', 'or', 'in', 'for', 'with']:
                product_terms.append(word)
        
        return {
            'industries': detected_industries,
            'product_terms': list(set(product_terms))
        }

    def generate_pain_point_queries(self, pain_point: str, industry_info: Dict) -> List[str]:
        """
        Generate queries focused on pain point solutions for any industry
        """
        industries = industry_info['industries']
        product_terms = industry_info['product_terms']
        
        # Create industry-specific query templates
        templates = [
            "how brands solve {pain} in {industry}",
            "{industry} solutions for {pain}",
            "{industry} best practices {pain}",
            "successful solutions for {pain} in {industry}",
            "marketing strategies addressing {pain} {industry}",
            "customer satisfaction {pain} {industry}",
            "innovation solving {pain} {industry}"
        ]
        
        queries = []
        for industry in industries:
            for template in templates:
                query = template.format(
                    pain=pain_point.lower(),
                    industry=industry
                )
                queries.append(query)
        
        # Add product-specific queries if available
        if product_terms:
            product_templates = [
                f"how to solve {pain_point} in {' '.join(product_terms)}",
                f"{' '.join(product_terms)} {pain_point} solutions",
                f"improving {pain_point} in {' '.join(product_terms)}"
            ]
            queries.extend(product_templates)
        
        return queries

    def generate_competitor_queries(self, competitor: str, industry_info: Dict) -> List[str]:
        """
        Generate competitor analysis queries for any industry
        """
        industries = industry_info['industries']
        product_terms = industry_info['product_terms']
        
        base_queries = [
            f"{competitor} market share",
            f"{competitor} brand strategy",
            f"{competitor} marketing campaigns",
            f"{competitor} target audience",
            f"{competitor} product portfolio",
            f"{competitor} pricing strategy",
            f"{competitor} customer reviews",
            f"{competitor} brand positioning"
        ]
        
        # Add industry-specific queries
        industry_queries = []
        for industry in industries:
            industry_queries.extend([
                f"{competitor} {industry} market analysis",
                f"{competitor} {industry} market share",
                f"{competitor} position in {industry} market",
                f"{competitor} {industry} strategy"
            ])
        
        # Add product-specific queries if available
        product_queries = []
        if product_terms:
            product_text = ' '.join(product_terms)
            product_queries = [
                f"{competitor} {product_text} analysis",
                f"{competitor} {product_text} reviews",
                f"{competitor} {product_text} market"
            ]
        
        return base_queries + industry_queries + product_queries

    def generate_market_queries(self, media_insights: Dict, industry_info: Dict) -> List[str]:
        """
        Generate market analysis queries for any industry
        """
        industries = industry_info['industries']
        product_terms = industry_info['product_terms']
        audience = media_insights.get('primaryAudienceDemographics', '').lower()
        
        base_queries = []
        for industry in industries:
            base_queries.extend([
                f"{industry} market trends",
                f"{industry} industry analysis",
                f"{industry} consumer behavior",
                f"{industry} market segmentation",
                f"{industry} growth opportunities",
                f"{industry} market challenges"
            ])
        
        # Add audience-specific queries
        if audience:
            audience_queries = [
                f"{industry} products for {audience}",
                f"{audience} preferences in {industry}",
                f"{industry} marketing to {audience}"
            ]
            base_queries.extend(audience_queries)
        
        # Add product-specific queries
        if product_terms:
            product_text = ' '.join(product_terms)
            product_queries = [
                f"{product_text} market analysis",
                f"{product_text} consumer trends",
                f"{product_text} industry outlook"
            ]
            base_queries.extend(product_queries)
        
        return base_queries

    def generate_search_queries(self, media_insights: Dict) -> Dict[str, List[str]]:
        """
        Generate all search queries based on media insights
        """
        # Extract industry information first
        industry_info = self.extract_industry_terms(media_insights)
        
        queries = {
            'competitor_analysis': [],
            'pain_point_solutions': [],
            'market_strategy': []
        }
        
        # Generate competitor queries
        for competitor in media_insights.get('competitors', []):
            queries['competitor_analysis'].extend(
                self.generate_competitor_queries(competitor, industry_info)
            )
        
        # Generate pain point queries
        for pain_point in media_insights.get('painPointsAddressed', []):
            queries['pain_point_solutions'].extend(
                self.generate_pain_point_queries(pain_point, industry_info)
            )
        
        # Generate market strategy queries
        queries['market_strategy'] = self.generate_market_queries(media_insights, industry_info)
        
        return queries

    def search_youtube(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search YouTube using direct search
        """
        try:
            print(f"Starting YouTube search for query: {query}")
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            print(f"Making request to YouTube: {url}")
            response = requests.get(url, headers=self.headers)
            print(f"YouTube response status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"YouTube error: Status code {response.status_code}")
                print(f"Response content: {response.text[:500]}")  # Print first 500 chars of error
                return []
                
            # Extract video IDs using string manipulation
            content = response.text
            videos = []
            start = 0
            
            while len(videos) < max_results:
                # Find videoId in the response
                vid_index = content.find('"videoId":"', start)
                if vid_index == -1:
                    break
                    
                vid_start = vid_index + 11
                vid_end = content.find('"', vid_start)
                video_id = content[vid_start:vid_end]
                
                # Find title
                title_index = content.find('"title":{"runs":[{"text":"', vid_end)
                if title_index == -1:
                    title_index = content.find('"title":{"simpleText":"', vid_end)
                    if title_index == -1:
                        start = vid_end
                        continue
                    title_start = title_index + 23
                else:
                    title_start = title_index + 26
                title_end = content.find('"', title_start)
                title = content[title_start:title_end]
                
                # Find channel name
                channel_index = content.find('"ownerText":{"runs":[{"text":"', title_end)
                if channel_index == -1:
                    channel = "N/A"
                else:
                    channel_start = channel_index + 28
                    channel_end = content.find('"', channel_start)
                    channel = content[channel_start:channel_end]
                
                if video_id and title and not any(v['url'].endswith(video_id) for v in videos):
                    video_info = {
                        'title': urllib.parse.unquote(title),
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'channel': channel,
                        'thumbnail': f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                        'category': self.categorize_query(query),
                        'query': query
                    }
                    videos.append(video_info)
                    print(f"Added video: {video_info['title']}")
                
                start = title_end
            
            if not videos:
                print(f"No videos found for query: {query}")
            else:
                print(f"\nFound {len(videos)} videos for '{query}':")
                for video in videos:
                    print(f"  Title: {video['title']}")
                    print(f"  URL: {video['url']}")
                    print(f"  Channel: {video['channel']}")
                    print("  " + "-"*30)
            
            return videos
            
        except Exception as e:
            print(f"Error in YouTube search: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return []

    def search_news_api(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search using NewsAPI with improved query handling
        """
        try:
            print(f"Starting NewsAPI search for query: {query}")
            # Calculate date range (last 6 months)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            # Format dates for API
            from_date = start_date.strftime('%Y-%m-%d')
            to_date = end_date.strftime('%Y-%m-%d')
            
            # Expand query with relevant terms
            expanded_query = f"{query} OR ({query} market share) OR ({query} sales) OR ({query} revenue) OR ({query} growth)"
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': expanded_query,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': max_results * 2,  # Request more results to filter
                'from': from_date,
                'to': to_date,
                'apiKey': self.news_api_key
            }
            
            print(f"Making request to NewsAPI: {url} with params {params}")
            response = requests.get(url, params=params)
            print(f"NewsAPI response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if data.get('articles'):
                    print(f"\nFound news articles for '{query}':")
                    
                    for article in data.get('articles', []):
                        # Skip articles with no content
                        if not article.get('description') or not article.get('title'):
                            continue
                            
                        result = {
                            'title': article.get('title', ''),
                            'link': article.get('url', ''),
                            'snippet': article.get('description', 'No description available'),
                            'source': article.get('source', {}).get('name', 'Unknown'),
                            'published': article.get('publishedAt', ''),
                            'category': self.categorize_query(query),
                            'query': query,
                            'author': article.get('author', 'Unknown')
                        }
                        
                        # Only add if it seems relevant (basic relevance check)
                        if any(term.lower() in result['title'].lower() or term.lower() in result['snippet'].lower() 
                              for term in ['jbl', 'harman', 'audio', 'market', 'india', 'speaker', 'headphone']):
                            results.append(result)
                            print(f"Added article: {result['title']}")
                            print(f"  Title: {result['title']}")
                            print(f"  Source: {result['source']}")
                            print(f"  URL: {result['link']}")
                            print(f"  Published: {result['published']}")
                            print("  " + "-"*30)
                            
                            if len(results) >= max_results:
                                break
                    
                    if not results:
                        print("No relevant articles found")
                
                return results
            else:
                print(f"NewsAPI request failed with status code: {response.status_code}")
                if response.status_code == 429:
                    print("Rate limit exceeded. Please try again later.")
                return []
                
        except Exception as e:
            print(f"Error in News API search: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return []

    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search news using Google News RSS feed
        """
        try:
            print(f"Starting Google News search for query: {query}")
            encoded_query = urllib.parse.quote(query)
            url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
            
            print(f"Making request to Google News: {url}")
            feed = feedparser.parse(url)
            results = []
            
            if feed.entries:
                print(f"\nFound news articles for '{query}':")
                
                for entry in feed.entries[:max_results]:
                    result = {
                        'title': entry.title,
                        'link': entry.link,
                        'snippet': entry.description if hasattr(entry, 'description') else entry.title,
                        'source': entry.source.title if hasattr(entry, 'source') else 'Google News',
                        'published': entry.published if hasattr(entry, 'published') else 'N/A',
                        'category': self.categorize_query(query),
                        'query': query
                    }
                    
                    # Only add if it seems relevant
                    if any(term.lower() in result['title'].lower() or term.lower() in result['snippet'].lower() 
                          for term in ['jbl', 'harman', 'audio', 'market', 'india', 'speaker', 'headphone']):
                        results.append(result)
                        print(f"Added article: {result['title']}")
                        print(f"  Title: {result['title']}")
                        print(f"  Source: {result['source']}")
                        print(f"  URL: {result['link']}")
                        print(f"  Published: {result['published']}")
                        print("  " + "-"*30)
                
                if not results:
                    print("No relevant articles found")
            
            return results
            
        except Exception as e:
            print(f"Error in news search: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return []

    def search_reddit(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search Reddit using their JSON API
        """
        try:
            print(f"Starting Reddit search for query: {query}")
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.reddit.com/search.json?q={encoded_query}&sort=relevance&limit={max_results}"
            
            print(f"Making request to Reddit API: {url}")
            response = requests.get(url, headers=self.headers)
            print(f"Reddit API response status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Reddit API error: Status code {response.status_code}")
                print(f"Response content: {response.text[:500]}")  # Print first 500 chars of error
                return []
            
            data = response.json()
            results = []
            
            if 'data' in data and 'children' in data['data']:
                posts = data['data']['children']
                print(f"Found {len(posts)} Reddit posts")
                
                for post in posts:
                    post_data = post['data']
                    result = {
                        'title': post_data.get('title', ''),
                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                        'source': 'reddit',
                        'score': post_data.get('score', 0),
                        'created_utc': post_data.get('created_utc', 0)
                    }
                    results.append(result)
                    print(f"Added post: {result['title']}")
            else:
                print(f"Unexpected Reddit API response structure: {data.keys()}")
            
            return results
            
        except Exception as e:
            print(f"Error in Reddit search: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return []

    def search_medium(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search Medium articles using web scraping
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing article information
        """
        try:
            print(f"Starting Medium search for query: {query}")
            search_url = f"https://medium.com/search?q={query}"
            
            print(f"Making request to Medium: {search_url}")
            response = requests.get(search_url, headers=self.headers)
            print(f"Medium response status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Medium error: Status code {response.status_code}")
                print(f"Response content: {response.text[:500]}")  # Print first 500 chars of error
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            # Find article elements - Medium uses article tags for posts
            articles = soup.find_all('article', limit=max_results)
            
            for article in articles:
                # Extract article information
                title_elem = article.find('h2')
                link_elem = article.find('a', href=True)
                author_elem = article.find('div', {'class': 'ae'})  # Medium's author class
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem['href']
                    if not url.startswith('http'):
                        url = f"https://medium.com{url}"
                        
                    author = author_elem.get_text().strip() if author_elem else "Unknown Author"
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'author': author,
                        'source': 'medium'
                    })
                    print(f"Added article: {title}")
                    
            return results[:max_results]
            
        except Exception as e:
            print(f"Error searching Medium: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return []

    def categorize_query(self, query: str):
        """
        Categorize the query based on its content
        """
        query = query.lower()
        if any(term in query for term in ['marketing strategy', 'campaign', 'brand']):
            return 'Marketing Strategy'
        elif any(term in query for term in ['case study', 'analysis', 'success story']):
            return 'Case Study'
        elif any(term in query for term in ['solve', 'solution', 'addressing']):
            return 'Problem Solution'
        else:
            return 'General'

    def find_targeted_content(self, media_insights: Dict, max_results_per_query: int = 3,
                         max_total_results: int = 50,
                         max_queries_per_category: int = 5) -> Dict:
        """
        Find targeted content using multiple sources with clear limits
        
        Args:
            media_insights: Dictionary containing market research data
            max_results_per_query: Maximum results to fetch per individual query
            max_total_results: Maximum total results across all sources
            max_queries_per_category: Maximum number of queries to use per category
        """
        results = {
            'youtube_videos': [],
            'news_articles': [],
            'reddit_posts': [],
            'medium_articles': [],
            'total_items': 0,
            'stats': {
                'queries_generated': 0,
                'queries_used': 0,
                'total_results_found': 0
            }
        }

        # Generate and limit queries
        all_queries = self.generate_search_queries(media_insights)
        results['stats']['queries_generated'] = sum(len(queries) for queries in all_queries.values())

        # Limit queries per category
        for category in all_queries:
            all_queries[category] = all_queries[category][:max_queries_per_category]
        
        results['stats']['queries_used'] = sum(len(queries) for queries in all_queries.values())
        
        # Process each category of queries
        for category, queries in all_queries.items():
            print(f"\nProcessing {category} queries...")
            
            for query in queries:
                # Check if we've hit the total limit
                if results['total_items'] >= max_total_results:
                    print(f"\nReached maximum total results limit ({max_total_results})")
                    break
                
                print(f"\nSearching for: {query}")
                
                # YouTube search with limits
                if len(results['youtube_videos']) < max_total_results:
                    videos = self.search_youtube(query, min(max_results_per_query,
                                                          max_total_results - len(results['youtube_videos'])))
                    results['youtube_videos'].extend(videos)
                
                # News search with limits
                if len(results['news_articles']) < max_total_results:
                    news = self.search_news(query, min(max_results_per_query,
                                                     max_total_results - len(results['news_articles'])))
                    results['news_articles'].extend(news)
                
                # Reddit search with limits
                if len(results['reddit_posts']) < max_total_results:
                    posts = self.search_reddit(query, min(max_results_per_query,
                                                        max_total_results - len(results['reddit_posts'])))
                    results['reddit_posts'].extend(posts)
                
                # Medium search with limits
                if len(results['medium_articles']) < max_total_results:
                    articles = self.search_medium(query, min(max_results_per_query,
                                                           max_total_results - len(results['medium_articles'])))
                    results['medium_articles'].extend(articles)
                
                # Update total items
                results['total_items'] = (len(results['youtube_videos']) +
                                        len(results['news_articles']) +
                                        len(results['reddit_posts']) +
                                        len(results['medium_articles']))
                
                # Add delay between queries
                self._delay()
        
        # Final statistics
        results['stats']['total_results_found'] = results['total_items']
        
        # Print summary
        print("\nSearch Complete!")
        print(f"Queries Generated: {results['stats']['queries_generated']}")
        print(f"Queries Used: {results['stats']['queries_used']}")
        print(f"Total Results Found: {results['stats']['total_results_found']}")
        print(f"YouTube Videos: {len(results['youtube_videos'])}")
        print(f"News Articles: {len(results['news_articles'])}")
        print(f"Reddit Posts: {len(results['reddit_posts'])}")
        print(f"Medium Articles: {len(results['medium_articles'])}")
        
        return results

def main():
    # Test Medium article search directly
    print("\nTesting Medium Article Search...")
    print("Searching for 'artificial intelligence' articles...")
    finder = ContentFinder()
    medium_results = finder.search_medium("artificial intelligence", max_results=3)
    
    print("\nMedium Search Results:")
    print("-" * 50)
    for idx, article in enumerate(medium_results, 1):
        print(f"\n{idx}. Title: {article['title']}")
        print(f"   Author: {article['author']}")
        print(f"   URL: {article['url']}")
    print("-" * 50)

    # Example media insights for testing comprehensive search
    media_insights = {
        "primaryAudienceDemographics": "Urban Indian consumers aged 18-45, tech-savvy, food enthusiasts, working professionals and college students",
        "painPointsAddressed": [
            "Long delivery waiting times",
            "Inconsistent food quality",
            "High delivery charges",
            "Limited restaurant options in some areas",
            "Order cancellation issues"
        ],
        "competitors": [
            "Swiggy",
            "UberEats",
            "EatFit",
            "Dunzo",
            "FoodPanda"
        ],
        "marketPosition": "Leading food delivery and restaurant discovery platform providing diverse dining options with real-time tracking"
    }
    
    finder = ContentFinder()
    
    # Set clear limits
    results = finder.find_targeted_content(
        media_insights,
        max_results_per_query=3,    # Maximum 3 results per individual query
        max_total_results=50,       # Stop after finding 50 total items
        max_queries_per_category=5  # Use only top 5 queries from each category
    )

if __name__ == "__main__":
    main()
