import time

import geopapyrus
import timeit
import mocks
import random


class TestDistance:
    def test_distance_haversine_m_ok(self):
        res = geopapyrus.distance_haversine_m(
            55.793246, 37.799445, 55.803140, 37.798920
        )

        assert res == 1100.3792724609375

    def test_distance_haversine_medium_ok(self):
        res = geopapyrus.distance_haversine_m(
            55.793246, 37.799445, 55.759694, 37.573519
        )

        assert res == 14613.396484375

    def test_distance_haversine_big_ok(self):
        res = geopapyrus.distance_haversine_m(
            55.793246, 37.799445, 53.361012, 58.958361
        )

        assert res == 1384479.25

    def test_distance_geodesic_m_ok(self):
        res = geopapyrus.distance_geodesic_m(
            55.793246, 37.799445, 55.803140, 37.798920
        )

        assert res == 1102.0716946693653

    def test_distance_geodesic_medium_ok(self):
        res = geopapyrus.distance_geodesic_m(
            55.793246, 37.799445, 55.759694, 37.573519
        )

        assert res == 14661.282745701496

    def test_distance_geodesic_big_ok(self):
        res = geopapyrus.distance_geodesic_m(
            55.793246, 37.799445, 53.361012, 58.958361
        )

        assert res == 1388998.3696851355


class TestPerformance:
    def test_distance_haversine_big_ok(self):
        print()
        amount = 1_000_000

        p_times = 0
        r_haversine_times = 0
        r_geodesic_times = 0
        for i in range(amount):
            lat1 = random.random() * 90
            lat2 = random.random() * 90
            lon1 = random.random() * 90
            lon2 = random.random() * 90

            t0 = time.monotonic()
            mocks.distance_haversine_m(lat1, lon1, lat2, lon2)
            p_times += time.monotonic() - t0

            t0 = time.monotonic()
            geopapyrus.distance_haversine_m(lat1, lon1, lat2, lon2)
            r_haversine_times += time.monotonic() - t0

            t0 = time.monotonic()
            geopapyrus.distance_geodesic_m(lat1, lon1, lat2, lon2)
            r_geodesic_times += time.monotonic() - t0

        print("python", p_times / amount * 1000 * 1000, "ns")
        print("rust_haversine", r_haversine_times / amount * 1000 * 1000, "ns")
        print("rust_geodesic", r_haversine_times / amount * 1000 * 1000, "ns")
