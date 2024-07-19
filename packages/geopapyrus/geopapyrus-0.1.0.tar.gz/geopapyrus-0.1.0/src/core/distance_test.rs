#[cfg(test)]
mod tests {
    use crate::core::distance;
    #[test]
    fn test_distance_haversine_small_ok(){
        let res = distance::distance_haversine_m(55.793246, 37.799445, 55.803140, 37.798920);

        assert_eq!(res, 1100.3793)
    }


    #[test]
    fn test_distance_haversine_medium_ok(){
        let res = distance::distance_haversine_m(55.793246, 37.799445, 55.759694, 37.573519);

        assert_eq!(res, 14613.396)
    }

    #[test]
    fn test_distance_haversine_big_ok(){
        let res = distance::distance_haversine_m(55.793246, 37.799445, 53.361012, 58.958361);

        assert_eq!(res, 1384479.3)
    }

    #[test]
    fn test_distance_geodesic_small_ok(){
        let res = distance::distance_geodesic_m(55.793246, 37.799445, 55.803140, 37.798920);

        assert_eq!(res, 1102.0716946693653)
    }


    #[test]
    fn test_distance_geodesic_medium_ok(){
        let res = distance::distance_geodesic_m(55.793246, 37.799445, 55.759694, 37.573519);

        assert_eq!(res, 14661.282745701496)
    }

    #[test]
    fn test_distance_geodesic_big_ok(){
        let res = distance::distance_geodesic_m(55.793246, 37.799445, 53.361012, 58.958361);

        assert_eq!(res, 1388998.3696851355)
    }
}