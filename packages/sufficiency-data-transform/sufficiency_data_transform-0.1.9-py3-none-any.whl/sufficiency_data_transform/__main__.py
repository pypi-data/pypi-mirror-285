from sufficiency_data_transform.all_dim_and_fact import (
    create_dimONSArea,
    create_dimLookedAfterChild,
    create_dimOfstedProvider,
    create_dimPostcode,
    create_factEpisode,
    create_factOfstedInspection,
    create_dim_tables,
)

if __name__ == "__main__":
    create_dim_tables()
    create_dimONSArea()
    create_dimLookedAfterChild()
    create_dimOfstedProvider()
    create_dimPostcode()
    create_factEpisode()
    create_factOfstedInspection()
