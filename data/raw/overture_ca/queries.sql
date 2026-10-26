-- The raw_glob path is local to this run.
CREATE VIEW raw_places AS SELECT * FROM read_parquet('data/raw/overture_ca/raw_shards/*.parquet');

CREATE TEMP VIEW base_points AS 
            SELECT id, names.primary AS name, basic_category,
                   taxonomy.primary AS category, taxonomy.hierarchy AS hierarchy,
                   taxonomy.alternates AS alternate_categories,
                   confidence, operating_status,
                   audit_lon AS lon, audit_lat AS lat,
                   addresses, sources, brand, websites, phones,
                   audit_source_file, audit_release, audit_scope,
                   coalesce(confidence >= 0.8, false)
                   AND trim(coalesce(names.primary, '')) <> ''
                   AND taxonomy.primary IS NOT NULL
                   AND coalesce(operating_status NOT IN
                       ('temporarily_closed', 'permanently_closed'), true)
                   AS passes_initial_quality_screen
            FROM raw_places
        ;

CREATE VIEW points AS 
            SELECT *, coalesce(list_extract(hierarchy, 2) IN ['department_store', 'discount_store', 'fashion_and_apparel_store', 'second_hand_store', 'specialty_store'], false) AND NOT coalesce(list_has_any(hierarchy, ['adult_store', 'auction_house', 'building_supply_store', 'car_stereo_store', 'electrical_supply_store', 'farming_equipment_and_supply_store', 'flea_market', 'gun_and_ammo_store', 'hardware_home_and_garden_store', 'junkyard', 'livestock_feed_and_supply_store', 'medical_supply_store', 'personal_shopper', 'pharmacy_and_drug_store', 'pick_your_own_farm', 'pop_up_store', 'safety_equipment_store', 'smoke_and_vape_store', 'tactical_supply_store', 'vehicle_parts_store', 'video_and_video_game_rental', 'welding_supply_store', 'woodworking_supply_store']), false) AS in_candidate_category_frame,
                   
            CASE WHEN category IN ['toy_store', 'toys_and_games_store'] THEN 'strict_category_proxy'
                 WHEN category IN ['hobby_shop', 'comic_books_store', 'tabletop_games_store', 'video_game_store', 'arts_crafts_and_hobby_store'] THEN 'ambiguous_category'
                 WHEN regexp_matches(coalesce(name, ''),
                    '(?i)pop[ -]?mart|blind[ -]?box|collectibl|designer[ -]?toys')
                 THEN 'name_keyword_only' ELSE NULL END
         AS target_review_reason,
                   coalesce(category IN ['toy_store', 'toys_and_games_store'], false)
                   AS is_strict_target_proxy
            FROM base_points
        ;

-- Candidate frame, not an approved/cleaned California sample:

            SELECT *, CASE WHEN is_strict_target_proxy THEN 1 ELSE 0 END AS label_proxy
            FROM points
            WHERE passes_initial_quality_screen AND in_candidate_category_frame
              AND (target_review_reason IS NULL OR is_strict_target_proxy)
        ;

-- Manual label audit queue:
SELECT * FROM points WHERE target_review_reason IS NOT NULL;
