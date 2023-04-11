from .toppop import TopPop
from .random import Random
from .indexed import Indexed
from .recommender import Recommender
import random


class MyRecommender(Recommender):
    """
    Recommend tracks closest to the previous one.
    Fall back to the random recommender if no
    recommendations found for the track.
    """

    def __init__(self, tracks_redis, catalog, recommendations_redis, last_fav_song):
        self.tracks_redis = tracks_redis
        #self.fallback = TopPop(tracks_redis, catalog.top_tracks[:100])
        self.fallback = Random(tracks_redis)
        #self.fallback = Indexed(tracks_redis, recommendations_redis, catalog)
        self.catalog = catalog
        self.last_fav_song = last_fav_song

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if user not in self.last_fav_song:
            self.last_fav_song[user] = prev_track

        last_fav_track = self.last_fav_song[user]
        previous_track = self.tracks_redis.get(last_fav_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]


