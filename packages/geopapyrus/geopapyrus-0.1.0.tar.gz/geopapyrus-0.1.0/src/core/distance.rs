use geo::point;
use geo::GeodesicDistance;
use geo::HaversineDistance;

pub fn distance_haversine_m(lat1: f32, lon1: f32, lat2: f32, lon2: f32) -> f32 {
    let p1 = point!(x: lon1, y:lat1);
    let p2 = point!(x: lon2, y:lat2);
    return p1.haversine_distance(&p2);
}

pub fn distance_geodesic_m(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    let p1 = point!(x: lon1, y:lat1);
    let p2 = point!(x: lon2, y:lat2);

    return p1.geodesic_distance(&p2);
}