job_configs = {
    sdb_den_helder = {
        description = "Job to generate the SDB of the area around Den Helder, NL",
        cron_schedule = "0 1 1 */3 *",  # 01:00 every 3rd month (March / June / September / December)
        time_zone = "Europe/Amsterdam",
        http_method = "POST",
        uri = "https://europe-west1-bathymetry.cloudfunctions.net/export-tile-bathymetry",  # TODO: get this output in terraform
        coordinates = [
                [
                    4.726555204480136,
                    52.79894952106581
                ],
                [
                    5.382988309948886,
                    53.2615577684405
                ],
                [
                    5.226433134167636,
                    53.48931215536743
                ],
                [
                    4.770500516980136,
                    53.41898585234949
                ],
                [
                    4.270622587292636,
                    52.91018589685636
                ],
                [
                    4.726555204480136,
                    52.79894952106581
                ]
            ]
        zoom = 10,
        step_months = 3,
        window_years = 1,
    }
}
