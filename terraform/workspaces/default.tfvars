sdb_job_configs = {
    sdb_den_helder = {
        description = "Job to generate the SDB of the area around Den Helder, NL",
        cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
        time_zone = "Europe/Amsterdam",
        http_method = "POST",
        uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",  # TODO: get this output in terraform
        coordinates = [
            [
                5.795880648281493,
                51.52322043928555
            ],
            [
                7.597638460781493,
                52.60383266102908
            ],
            [
                10.014630648281493,
                53.38409943602731
            ],
            [
                10.168439242031493,
                54.26597908534566
            ],
            [
                9.245587679531493,
                56.0604912541101
            ],
            [
                7.092267367031493,
                56.207423002919064
            ],
            [
                7.158185335781493,
                55.09168342821415
            ],
            [
                6.608868929531493,
                54.59827676009737
            ],
            [
                3.928204867031493,
                54.16319085617696
            ],
            [
                2.368146273281493,
                52.25550015782851
            ],
            [
                2.434064242031493,
                51.16637724261702
            ],
            [
                3.642560335781493,
                50.80675167573701
            ],
            [
                5.795880648281493,
                51.52322043928555
            ]
        ],
        zoom = 9,
        export_zoom = 13,
        step_months = 3,
        window_years = 2,
        asset_path = "projects/deltares-rws/eo-bathymetry/test-collection"
    }
}

rgb_job_configs = {
    rgb_den_helder = {
        coordinates = [
            [
                5.795880648281493,
                51.52322043928555
            ],
            [
                7.597638460781493,
                52.60383266102908
            ],
            [
                10.014630648281493,
                53.38409943602731
            ],
            [
                10.168439242031493,
                54.26597908534566
            ],
            [
                9.245587679531493,
                56.0604912541101
            ],
            [
                7.092267367031493,
                56.207423002919064
            ],
            [
                7.158185335781493,
                55.09168342821415
            ],
            [
                6.608868929531493,
                54.59827676009737
            ],
            [
                3.928204867031493,
                54.16319085617696
            ],
            [
                2.368146273281493,
                52.25550015782851
            ],
            [
                2.434064242031493,
                51.16637724261702
            ],
            [
                3.642560335781493,
                50.80675167573701
            ],
            [
                5.795880648281493,
                51.52322043928555
            ]
        ],
        description = "Job to generate the SDB of the area around Den Helder, NL",
        cron_schedule = "0 1 2 */3 *",  # 01:00 the 2nd day of every 3rd month (March / June / September / December)
        time_zone = "Europe/Amsterdam",
        http_method = "POST",
        uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",  # TODO: get this output in terraform
        min_zoom = 0,
        max_zoom = 13
    }
}
