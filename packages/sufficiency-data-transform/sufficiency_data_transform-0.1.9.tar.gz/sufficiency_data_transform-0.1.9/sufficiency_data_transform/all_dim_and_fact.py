import pandas as pd
from decouple import config
from sufficiency_data_transform.dim_maps import (
    category_of_need,
    legal_status,
    ofsted_effectiveness,
    placement_provider,
    placement_type,
    reason_episode_ceased,
    reason_for_new_episode,
    reason_place_change,
)
from sufficiency_data_transform.maps import (
    ons_map,
    dimLookedAfterChild_columns_map,
    gender_map,
    ethnic_description_map,
    uasc_status_map,
    ofsted_provider_map,
    ofsted_to_ons_map,
    postcodes_map,
    episodes_map,
    inspection_map,
)
from sufficiency_data_transform.utils import (
    generate_dim,
    add_nan_row,
    fillna_date_columns,
    fillna_key_columns,
    fillna_cat_columns,
    fillna_num_columns,    
    open_file,
    open_location,
    write_csv,
)

output_location = config("OUTPUT_LOCATION")
input_location_ext = config("INPUT_LOCATION_EXT")
input_location_903 = config("INPUT_LOCATION_903")
input_location_ofs = config("INPUT_LOCATION_OFS")


def create_dim_tables():
    """Create lookup tables"""
    fs_out = open_location(output_location)
    generate_dim(category_of_need, "dimCategoryOfNeed.csv", fs_out)
    generate_dim(legal_status, "dimLegalStatus.csv", fs_out)
    generate_dim(ofsted_effectiveness, "dimOfstedEffectiveness.csv", fs_out)
    generate_dim(placement_provider, "dimPlacementProvider.csv", fs_out)
    generate_dim(placement_type, "dimPlacementType.csv", fs_out)
    generate_dim(reason_episode_ceased, "dimReasonEpisodeCeased.csv", fs_out)
    generate_dim(reason_for_new_episode, "dimReasonForNewEpisode.csv", fs_out)
    generate_dim(reason_place_change, "dimReasonPlaceChange.csv", fs_out)


def create_dimONSArea():
    fs_ext = open_location(input_location_ext)
    fs_out = open_location(output_location)

    ons_area = open_file(fs_ext, "ONS_Area.csv")

# Rename columns based on data model
    ons_area.rename(columns=ons_map, inplace=True)
    ons_area = ons_area[ons_map.values()]

# Creating AreaType, AreaCode and AreaName fields to allow a single primary key to access all area types
    ward_df = ons_area
    ward_df["AreaType"] = "Ward"
    ward_df["AreaCode"] = ward_df["WardCode"]
    ward_df["AreaName"] = ward_df["WardName"]

    la_df = ons_area[
        [
            "LACode",
            "LAName",
            "CountyCode",
            "CountyName",
            "RegionCode",
            "RegionName",
            "CountryCode",
            "CountryName",
        ]
    ]
    la_df.loc[~la_df["LACode"].isna(), "AreaType"] = "LA" 
    la_df.loc[~la_df["LACode"].isna(), "AreaCode"] = la_df["LACode"]
    la_df.loc[~la_df["LACode"].isna(), "AreaName"] = la_df["LAName"]

    county_df = ons_area[
        [
            "CountyCode",
            "CountyName",
            "RegionCode",
            "RegionName",
            "CountryCode",
            "CountryName",
        ]
    ]
    county_df.loc[~county_df["CountyCode"].isna(), "AreaType"] = "County"
    county_df.loc[~county_df["CountyCode"].isna(), "AreaCode"] = county_df["CountyCode"]
    county_df.loc[~county_df["CountyCode"].isna(), "AreaName"] = county_df["CountyName"]

    region_df = ons_area[
        [
            "RegionCode",
            "RegionName",
            "CountryCode",
            "CountryName",
        ]
    ]
    region_df.loc[~region_df["RegionCode"].isna(), "AreaType"] = "Region"
    region_df.loc[~region_df["RegionCode"].isna(), "AreaCode"] = region_df["RegionCode"]
    region_df.loc[~region_df["RegionCode"].isna(), "AreaName"] = region_df["RegionName"]

    country_df = ons_area[
        [
            "CountryCode",
            "CountryName",
        ]
    ]
    country_df.loc[~country_df["CountryCode"].isna(), "AreaType"] = "Country"
    country_df.loc[~country_df["CountryCode"].isna(), "AreaCode"] = country_df["CountryCode"]
    country_df.loc[~country_df["CountryCode"].isna(), "AreaName"] = country_df["CountryName"]

# Joining together into a single file and dropping duplicates and rows with no AreaType defined
    dimONSArea = pd.concat(
        [ward_df, la_df, county_df, region_df, country_df]
    ).drop_duplicates()
    dimONSArea.dropna(subset="AreaType", inplace=True)

# Reset indexes and use main index as primary key
    dimONSArea.reset_index(drop=True, inplace=True)
    dimONSArea.reset_index(inplace=True, names="ONSAreaKey")

# add a row to return when the lookup column is not matched
    dimONSArea = add_nan_row(dimONSArea)

# Replace missing values for key and date fields
    key_cols = [
        "ONSAreaKey",
    ]
    dimONSArea = fillna_key_columns(dimONSArea, key_cols)

    cat_cols = [
        "WardCode",
        "WardName",
        "LACode",
        "LAName",
        "CountyCode",
        "CountyName",
        "RegionCode",
        "RegionName",
        "CountryCode",
        "CountryName",
        "AreaType",
        "AreaCode",
        "AreaName",
    ]
    dimONSArea = fillna_cat_columns(dimONSArea, cat_cols)

    write_csv(dimONSArea, fs_out, "dimONSArea.csv", False)


def create_dimLookedAfterChild():
    """
    Creates table with unique entry for each LookedAfterChild with data on UASC merged
    """
    fs_903 = open_location(input_location_903)
    fs_out = open_location(output_location)

# Open header file and drop rows with no child identifier
    header = open_file(fs_903, "ssda903_Header.csv")
    header.dropna(subset="CHILD", inplace=True)

# Open UASC file and merge with header
    uasc = open_file(fs_903, "ssda903_UASC.csv")
    uasc = uasc[["CHILD", "DUC", "YEAR"]]
 
    dimLookedAfterChild = header.merge(
        uasc, on=["CHILD", "YEAR"], how="left"
    )

# Open ONS Area file with ONS codes and merge with dim file
    ons_area = open_file(fs_out, "dimONSArea.csv")
    ons_area = ons_area[["ONSAreaKey", "AreaName"]]
    dimLookedAfterChild = dimLookedAfterChild.merge(
        ons_area, left_on="LA", right_on="AreaName", how="left"
    )

# Rename columns to data model convention
    dimLookedAfterChild.rename(columns=dimLookedAfterChild_columns_map, inplace=True)
    dimLookedAfterChild = dimLookedAfterChild[dimLookedAfterChild_columns_map.values()]

# Reset indexes
    dimLookedAfterChild.reset_index(inplace=True, drop=True)
    dimLookedAfterChild.reset_index(inplace=True, names="LookedAfterChildKey")

# Create unknown child reference row
    dimLookedAfterChild = add_nan_row(dimLookedAfterChild)

# Replace missing values for key and date fields
    key_cols = [
        "LookedAfterChildKey",
        "Gender",
        "EthnicCode",
        "ONSAreaCode",
        "SubmissionYearDateKey",
    ]
    dimLookedAfterChild = fillna_key_columns(dimLookedAfterChild, key_cols)

    date_cols = [
        "DateofBirthKey",
        "UASCCeasedDateKey",
    ]
    dimLookedAfterChild = fillna_date_columns(dimLookedAfterChild, date_cols)

    cat_cols = [
        "ChildIdentifier",
    ]
    dimLookedAfterChild = fillna_cat_columns(dimLookedAfterChild, cat_cols)

# Replace numerical values in gender with strings
    dimLookedAfterChild["Gender"] = dimLookedAfterChild["Gender"].map(gender_map)

# Create new field with descriptions for ethnicity codes
    dimLookedAfterChild["EthnicDescription"] = dimLookedAfterChild.EthnicCode.map(ethnic_description_map)

# Generate additional UASC fields using UASCCeasedDDateKey
    dimLookedAfterChild["UASCStatusCode"] = dimLookedAfterChild.UASCCeasedDateKey.map(
        lambda x: 0 if x=="2999-12-31" else 1
    )
 
    dimLookedAfterChild["UASCStatusDescription"] = (
        dimLookedAfterChild.UASCStatusCode.map(uasc_status_map)
    )

# Write output file
    write_csv(dimLookedAfterChild, fs_out, "dimLookedAfterChild.csv", False)


def create_dimOfstedProvider():
    fs_ofs = open_location(input_location_ofs)
    fs_out = open_location(output_location)

# Find the number of years' data present in the folder
    directory_contents = fs_ofs.listdir("")
    year_list = [f[-6:-4] for f in directory_contents]
    unique_years = set(year_list)

# For each year, create a unique record for each provider and put in dictionary
    provider_df_dict = {}
    for year in unique_years:
        last_year = int(year) - 1

    # Open providers_in_year file
        providers_in_file = "Provider_level_in_year_20"f"{last_year}""-"f"{year}"".csv"
        providers_in_df = open_file(fs_ofs, providers_in_file)

    # Open closed file
        closed_file = "Closed_childrens_homes_31Mar"f"{year}"".csv"
        closed_df = open_file(fs_ofs, closed_file)

    # Merge on URN to add closure info to richer providers_in record
        providers_closed = providers_in_df.merge(closed_df, on="URN", how="outer")

    # Open providers_places file
        providers_places_file = "Providers_places_at_31_Aug_20"f"{year}"".csv"
        providers_places = open_file(fs_ofs, providers_places_file)

        # Concatenate providers_places with merged providers_closed df
        providers_places = providers_places.rename(columns={"Organisation name":"Organisation which owns the provider"})
        providers_df = pd.concat([providers_places, providers_closed])
        providers_df = providers_df.drop_duplicates(subset="URN", keep="first")

    # Add year to table and output to dictionary
        providers_df["Year"] = year
        provider_df_dict[year] = providers_df

# Across the years in the dictionary, concatenate to single file and drop duplicates
    dimOfstedProvider = pd.concat(provider_df_dict)
    dimOfstedProvider["UnknownSourceFlag"] = False
    dimOfstedProvider.sort_values(by="Year", ascending=False)
    dimOfstedProvider.drop_duplicates(subset="URN", inplace=True)

# Merge with ONS Area Table to add ONS Area Key
    dimOfstedProvider["Local authority"] = dimOfstedProvider["Local authority"].replace(
        ofsted_to_ons_map
    )

    ons_area = open_file(fs_out, "dimONSArea.csv")

    dimOfstedProvider = dimOfstedProvider.merge(
        ons_area, left_on="Local authority", right_on="AreaName", how="left"
    )

# Rename columns following data model values and drop all other columns
    dimOfstedProvider = dimOfstedProvider.rename(columns=ofsted_provider_map)
    dimOfstedProvider = dimOfstedProvider[ofsted_provider_map.values()]

# Reset indexes
    dimOfstedProvider.reset_index(inplace=True, drop=True)
    dimOfstedProvider.reset_index(inplace=True, names="OfstedProviderKey")

# Add nan rows: one for unmatched URNs, one for missing URNs and one for XXXXXXX (regional adoption agencies)
    unmatched_row = {col: None for col in dimOfstedProvider.columns}
    unmatched_row["OfstedProviderKey"] = -3
    unmatched_row["UnknownSourceFlag"] = True
    dimOfstedProvider.loc[len(dimOfstedProvider)] = unmatched_row

    raa_row = {col: None for col in dimOfstedProvider.columns}
    raa_row["OfstedProviderKey"] = -2
    raa_row["URN"] = "XXXXXXX"
    raa_row["ProviderType"] = "Regional Adoption Agency"
    raa_row["UnknownSourceFlag"] = True
    dimOfstedProvider.loc[len(dimOfstedProvider)] = raa_row

    missing_row = {col: None for col in dimOfstedProvider.columns}
    missing_row["OfstedProviderKey"] = -1
    missing_row["URN"] = "Missing"
    missing_row["UnknownSourceFlag"] = True
    dimOfstedProvider.loc[len(dimOfstedProvider)] = missing_row

    # Replace missing values
    date_columns = [
        "RegistrationDate",
        "ClosedDate",
        ]
    dimOfstedProvider = fillna_date_columns(dimOfstedProvider, date_columns)

    cat_columns = [
        "URN",
        "ProviderType",
        "Sector",
        "ProviderStatus",
        "ONSAreaCode",
        "OwnerName",
    ]
    dimOfstedProvider = fillna_cat_columns(dimOfstedProvider, cat_columns)

    num_cols = [
        "MaxUsers"
    ]
    dimOfstedProvider = fillna_num_columns(dimOfstedProvider, num_cols)

# Write csv
    write_csv(dimOfstedProvider, fs_out, "dimOfstedProvider.csv", False)


def create_dimPostcode():
    fs_ext = open_location(input_location_ext)
    fs_out = open_location(output_location)

    dimPostcode = open_file(
        fs_ext, "ONSPD_reduced_to_postcode_sector.csv"
    )

# Rename columns based on data model convention and drop unwanted columns
    dimPostcode = dimPostcode.rename(postcodes_map, axis=1)
    dimPostcode = dimPostcode[postcodes_map.values()]

# Reset indexex
    dimPostcode.reset_index(inplace=True, drop=True)
    dimPostcode.reset_index(inplace=True, names="PostcodeKey")

# Add nan row
    dimPostcode = add_nan_row(dimPostcode)

# Replace missing values
    key_cols = [
        "PostcodeKey",
    ]
    dimPostcode = fillna_key_columns(dimPostcode, key_cols)

    cat_cols = [
        "Sector",
        "ONSAreaCode",
        "LSOA2011",
    ]
    dimPostcode = fillna_cat_columns(dimPostcode, cat_cols)

    num_cols = [
        "Latitude",
        "Longitude",
        "OSEastings",
        "OSNorthings",
        "IMD",
    ]
    dimPostcode = fillna_num_columns(dimPostcode, num_cols)

# Write output
    write_csv(dimPostcode, fs_out, "dimPostcode.csv", False)


def create_factEpisode():
    fs_903 = open_location(input_location_903)
    fs_out = open_location(output_location)

    episodes = open_file(fs_903, "ssda903_Episodes.csv")

    # LookedAfterChildKey
    looked_after_child = open_file(fs_out, "dimLookedAfterChild.csv")
    looked_after_child = looked_after_child[['LookedAfterChildKey', 'ChildIdentifier']]
    episodes = episodes.merge(
        looked_after_child, left_on="CHILD", right_on="ChildIdentifier", how="left"
    )

    # ReasonForNewEpisodeKey
    reason_for_new_episode = open_file(fs_out, "dimReasonForNewEpisode.csv")
    reason_for_new_episode = reason_for_new_episode[['ReasonForNewEpisodeKey', 'ReasonForNewEpisodeCode']]
    episodes = episodes.merge(
        reason_for_new_episode, left_on="RNE", right_on="ReasonForNewEpisodeCode", how="left"
    )

    # LegalStatusKey
    legal_status = open_file(fs_out, "dimLegalStatus.csv")
    legal_status = legal_status[['LegalStatusKey', 'LegalStatusCode']]
    episodes = episodes.merge(
        legal_status, left_on="LS", right_on="LegalStatusCode", how="left"
    )

    # CategoryOfNeedKey
    category_of_need = open_file(fs_out, "dimCategoryOfNeed.csv")
    category_of_need = category_of_need[['CategoryOfNeedKey', 'CategoryOfNeedCode']]
    episodes = episodes.merge(
        category_of_need, left_on="CIN", right_on="CategoryOfNeedCode", how="left"
    )

    # PlacementTypeKey
    placement_type = open_file(fs_out, "dimPlacementType.csv")
    placement_type = placement_type[['PlacementTypeKey', 'PlacementTypeCode']]
    episodes = episodes.merge(
        placement_type, left_on="PLACE", right_on="PlacementTypeCode", how="left"
    )

    # PlacementProviderKey
    placement_provider = open_file(fs_out, "dimPlacementProvider.csv")
    placement_provider = placement_provider[['PlacementProviderKey', 'PlacementProviderCode']]
    episodes = episodes.merge(
        placement_provider, left_on="PLACE_PROVIDER", right_on="PlacementProviderCode", how="left"
    )

    # ReasonEpisodeCeasedKey
    reason_episode_ceased = open_file(fs_out, "dimReasonEpisodeCeased.csv")
    reason_episode_ceased = reason_episode_ceased[['ReasonEpisodeCeasedKey', 'ReasonEpisodeCeasedCode']]
    episodes = episodes.merge(
        reason_episode_ceased, left_on="REC", right_on="ReasonEpisodeCeasedCode", how="left"
    )

    # ReasonPlaceChangeKey
    reason_place_change = open_file(fs_out, "dimReasonPlaceChange.csv")
    reason_place_change = reason_place_change[['ReasonPlaceChangeKey', 'ReasonPlaceChangeCode']]
    episodes = episodes.merge(
        reason_place_change, left_on="REASON_PLACE_CHANGE", right_on="ReasonPlaceChangeCode", how="left"
    )

    # HomePostcodeKey
    postcode = open_file(fs_out, "dimPostcode.csv")
    postcode = postcode[["PostcodeKey", "Sector"]]
    episodes = episodes.merge(
        postcode, left_on="HOME_POST", right_on="Sector", how="left"
    )
    episodes = episodes.rename(columns={"PostcodeKey": "HomePostcodeKey"})

    # PlacementPostcodeKey
    episodes = episodes.merge(
        postcode, left_on="PL_POST", right_on="Sector", how="left"
    )
    episodes = episodes.rename(columns={"PostcodeKey": "PlacementPostcodeKey"})

    # OfstedProviderKey
    ofsted_provider = open_file(fs_out, "dimOfstedProvider.csv")
    ofsted_provider = ofsted_provider[['OfstedProviderKey', 'URN']]
    ofsted_provider.URN = ofsted_provider.URN.astype(str)
    episodes.URN = episodes.URN.astype(str)
    episodes = episodes.merge(
        ofsted_provider, left_on="URN", right_on="URN", how="left"
    )
    # Where no match with dimOfstedProvider, give a value of -3 to differentiate from missing URNs
    episodes.loc[
        (~episodes["URN"].isna()) & (episodes["OfstedProviderKey"].isna()),
        "OfstedProviderKey"
        ] = -3

    # ONSAreaKey
    ons_area = open_file(fs_out, "dimONSArea.csv")
    ons_area = ons_area[['ONSAreaKey', 'AreaName']]
    episodes = episodes.merge(
        ons_area, left_on="LA", right_on="AreaName", how="left"
    )

    # Rename columns to data model convention
    episodes.rename(columns=episodes_map, inplace=True)
    episodes = episodes[episodes_map.values()]

    # Reset indexes
    episodes.reset_index(inplace=True, drop=True)
    episodes.reset_index(inplace=True, names="FactEpisodeKey")

    # Replace missing values
    episode_key_columns = [
        "LookedAfterChildKey",
        "ReasonForNewEpisodeKey",
        "LegalStatusKey",
        "CategoryOfNeedKey",
        "PlacementTypeKey",
        "PlacementProviderKey",
        "ReasonEpisodeCeasedKey",
        "ReasonPlaceChangeKey",
        "HomePostcodeKey",
        "PlacementPostcodeKey",
        "OfstedProviderKey",
        "ONSAreaKey",
        "SubmissionYearDateKey",
    ]
    episodes = fillna_key_columns(episodes, episode_key_columns)

    episode_date_columns = [
        "EpisodeCommencedDateKey",
        "EpisodeCeasedDateKey",        
    ]
    episodes = fillna_date_columns(episodes, episode_date_columns)

    write_csv(episodes, fs_out, "factEpisode.csv", False)


def create_factOfstedInspection():
    fs_out = open_location(output_location)
    fs_ofs = open_location(input_location_ofs)

# Find the number of years' data present in the folder
    directory_contents = fs_ofs.listdir("")
    year_list = [f[-6:-4] for f in directory_contents]
    unique_years = set(year_list)

# For each year, create a unique record for each provider and put in dictionary
    inspection_df_dict = {}
    for year in unique_years:
        last_year = int(year) - 1

    # Open provider at file
        provider_at_file = "Provider_level_at_31_Aug_20"f"{year}"".csv"
        provider_at_df = open_file(fs_ofs, provider_at_file)

    # Open providers_in_year file and keep only full inspections
        provider_in_file = "Provider_level_in_year_20"f"{last_year}""-"f"{year}"".csv"
        provider_in_df = open_file(fs_ofs, provider_in_file)
        provider_in_df = provider_in_df.loc[
            provider_in_df["Inspection event type"] == "Full inspection"
            ]

    # Concatenate providers_places with merged providers_closed df
        provider_at_df = provider_at_df.rename(columns={"Latest full inspection date":"Inspection date"})
        inspections_df = pd.concat([provider_at_df, provider_in_df])
        inspections_df = inspections_df.drop_duplicates(subset=["URN", "Inspection date"], keep="first")

    # Add year to table and output to dictionary
        inspections_df["Year"] = year
        inspection_df_dict[year] = inspections_df

# Across the years in the dictionary, concatenate to single file and drop duplicates
    factOfstedInspection = pd.concat(inspection_df_dict)
    factOfstedInspection.sort_values(by="Year", ascending=False)
    factOfstedInspection.drop_duplicates(subset=["URN", "Inspection date"], inplace=True)

# Merge with dim tables to replace key columns
    ofsted_provider = open_file(fs_out, "dimOfstedProvider.csv")
    ofsted_provider = ofsted_provider[["OfstedProviderKey", "URN"]]
    factOfstedInspection = factOfstedInspection.merge(
        ofsted_provider, how="left", on="URN"
    )

    ofsted_effectiveness = open_file(fs_out, "dimOfstedEffectiveness.csv")
    ofsted_effectiveness = ofsted_effectiveness[["OfstedEffectivenessKey", "OverallEffectiveness"]]
    factOfstedInspection = factOfstedInspection.merge(
        ofsted_effectiveness, how="left", left_on="Overall experiences and progress of children and young people", right_on="OverallEffectiveness"
    )

# Rename columns following data model values and drop all other columns
    factOfstedInspection = factOfstedInspection.rename(columns=inspection_map)
    factOfstedInspection = factOfstedInspection[inspection_map.values()]

# Create column that indicates if inspection is the most recent one recorded for a URN
    factOfstedInspection["IsLatest"] = (
        factOfstedInspection.groupby("OfstedProviderKey")["InspectionDateKey"].transform("max")
        == factOfstedInspection["InspectionDateKey"]
    )

# Create column that denotes the end date that an inspection applies to
# Sort to get providers and inspection dates in order
    factOfstedInspection.sort_values(
        by=["OfstedProviderKey", "InspectionDateKey"],
        inplace=True,
    )
# where isLatest is False, EndDateKey should be the next chronological inspection date for that URN
    factOfstedInspection.loc[~factOfstedInspection["IsLatest"], "EndDateKey"] = (
        factOfstedInspection["InspectionDateKey"].shift(-1)
    )

# Reset indexes and create episode index
    factOfstedInspection.reset_index(inplace=True, drop=True)
    factOfstedInspection.reset_index(inplace=True, names="factOfstedInspectionKey")

# Replace missing values
    key_cols = [
        "OfstedProviderKey",
        "OfstedEffectivenessKey",
    ]
    factOfstedInspection = fillna_key_columns(factOfstedInspection, key_cols)

    date_cols = [
        "InspectionDateKey",
        "EndDateKey",
    ]
    factOfstedInspection = fillna_date_columns(factOfstedInspection, date_cols)

# Write output
    write_csv(factOfstedInspection, fs_out, "factOfstedInspection.csv")