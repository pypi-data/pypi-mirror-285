import sys
import os
import awswrangler as wr

# SageWorks Imports
from sageworks.api.feature_set import FeatureSet
from sageworks.api.model import Model, ModelType
from sageworks.api.endpoint import Endpoint
from sageworks.utils.config_manager import ConfigManager
from sageworks.utils.glue_utils import glue_args_to_dict

# Convert Glue Job Args to a Dictionary
glue_args = glue_args_to_dict(sys.argv)

# Set the SAGEWORKS_BUCKET for the ConfigManager
cm = ConfigManager()
cm.set_config("SAGEWORKS_BUCKET", glue_args["--sageworks-bucket"])

# Feature Set Name (Hardcoded)
fs_name = "solubility_featurized_fs"

# Model Name (Hardcoded)
model_name = "solubility-class-0-nightly"

# Target and Feature List (Hardcoded)
target = ["class"]
features = [
    "estate_vsa3",
    "peoe_vsa3",
    "bertzct",
    "maxabspartialcharge",
    "smr_vsa6",
    "bcut2d_chghi",
    "smr_vsa2",
    "nhohcount",
    "fr_ether",
    "slogp_vsa4",
    "vsa_estate7",
    "numaromaticheterocycles",
    "minabsestateindex",
    "kappa1",
    "fr_piperdine",
    "maxestateindex",
    "fpdensitymorgan3",
    "fr_nh2",
    "fr_oxazole",
    "narombond",
    "smr_vsa8",
    "fr_sh",
    "fr_nitro",
    "fr_thiophene",
    "bcut2d_mwhi",
    "fr_ndealkylation1",
    "estate_vsa11",
    "labuteasa",
    "peoe_vsa10",
    "fpdensitymorgan1",
    "fr_oxime",
    "slogp_vsa6",
    "minestateindex",
    "kappa2",
    "fr_al_oh",
    "chi2n",
    "qed",
    "fr_c_o_nocoo",
    "fr_phenol_noorthohbond",
    "slogp_vsa5",
    "fr_thiazole",
    "apol",
    "fr_priamide",
    "vsa_estate6",
    "smr_vsa9",
    "slogp_vsa11",
    "bcut2d_mrlow",
    "fr_coo2",
    "fr_nitro_arom",
    "slogp_vsa7",
    "bcut2d_mwlow",
    "fr_alkyl_carbamate",
    "bpol",
    "fr_prisulfonamd",
    "estate_vsa9",
    "fr_thiocyan",
    "fr_nitro_arom_nonortho",
    "heavyatomcount",
    "numaliphaticrings",
    "vsa_estate10",
    "fr_aniline",
    "fr_quatn",
    "smr_vsa10",
    "fr_aldehyde",
    "numhdonors",
    "fr_hdrzine",
    "estate_vsa4",
    "fr_allylic_oxid",
    "fr_furan",
    "fr_term_acetylene",
    "fr_phos_acid",
    "bcut2d_chglo",
    "fr_c_s",
    "numheteroatoms",
    "fr_ar_coo",
    "fr_imine",
    "fr_nh0",
    "fr_piperzine",
    "estate_vsa5",
    "numsaturatedrings",
    "fr_al_oh_notert",
    "estate_vsa2",
    "chi0",
    "chi1n",
    "peoe_vsa12",
    "smr_vsa7",
    "vsa_estate8",
    "fr_phenol",
    "slogp_vsa9",
    "minpartialcharge",
    "numsaturatedheterocycles",
    "numaliphaticheterocycles",
    "fr_methoxy",
    "fr_aryl_methyl",
    "rotratio",
    "peoe_vsa6",
    "peoe_vsa13",
    "fr_para_hydroxylation",
    "fr_hdrzone",
    "fr_ar_nh",
    "fr_benzene",
    "smr_vsa1",
    "estate_vsa6",
    "numaromaticcarbocycles",
    "fr_guanido",
    "smr_vsa3",
    "minabspartialcharge",
    "smr_vsa5",
    "fr_nh1",
    "fr_imidazole",
    "vsa_estate1",
    "peoe_vsa4",
    "fr_halogen",
    "fr_epoxide",
    "fr_morpholine",
    "peoe_vsa5",
    "fr_c_o",
    "fr_ar_n",
    "fr_n_o",
    "fr_amidine",
    "fr_barbitur",
    "fr_hoccn",
    "heavyatommolwt",
    "exactmolwt",
    "vsa_estate9",
    "chi3n",
    "fr_coo",
    "fr_arn",
    "fr_isocyan",
    "fr_dihydropyridine",
    "tpsa",
    "fr_phos_ester",
    "maxabsestateindex",
    "fr_al_coo",
    "nrot",
    "slogp_vsa10",
    "slogp_vsa8",
    "fr_azo",
    "fr_sulfone",
    "numradicalelectrons",
    "estate_vsa7",
    "fr_ketone_topliss",
    "smr_vsa4",
    "fr_amide",
    "molmr",
    "molwt",
    "bcut2d_logplow",
    "bcut2d_mrhi",
    "fractioncsp3",
    "fr_bicyclic",
    "vsa_estate3",
    "bcut2d_logphi",
    "fr_azide",
    "fr_nitroso",
    "numvalenceelectrons",
    "slogp_vsa1",
    "chi2v",
    "fr_ketone",
    "estate_vsa1",
    "peoe_vsa2",
    "fr_lactam",
    "fr_nhpyrrole",
    "fr_unbrch_alkane",
    "numaromaticrings",
    "slogp_vsa3",
    "numaliphaticcarbocycles",
    "vsa_estate4",
    "fr_nitrile",
    "peoe_vsa7",
    "numrotatablebonds",
    "nocount",
    "fr_tetrazole",
    "chi4v",
    "fr_imide",
    "fpdensitymorgan2",
    "fr_sulfonamd",
    "chi4n",
    "kappa3",
    "fr_sulfide",
    "ringcount",
    "nbase",
    "balabanj",
    "fr_diazo",
    "peoe_vsa8",
    "vsa_estate5",
    "estate_vsa10",
    "chi3v",
    "estate_vsa8",
    "vsa_estate2",
    "chi0v",
    "fr_benzodiazepine",
    "fr_ester",
    "slogp_vsa12",
    "numhacceptors",
    "fr_urea",
    "chi1v",
    "maxpartialcharge",
    "slogp_vsa2",
    "fr_lactone",
    "fr_pyridine",
    "peoe_vsa14",
    "peoe_vsa9",
    "mollogp",
    "fr_ar_oh",
    "peoe_vsa1",
    "numsaturatedcarbocycles",
    "nacid",
    "fr_ndealkylation2",
    "chi0n",
    "naromatom",
    "fr_alkyl_halide",
    "chi1",
    "fr_isothiocyan",
    "hallkieralpha",
    "peoe_vsa11",
]


# Get FeatureSet
full_fs = FeatureSet(fs_name)

# placeholder for now will be using chem-utils helper function to verify tags
assay_type = "solubility"
tags_list = ["Nightly", f"assay:{assay_type}"]

################# CREATE MODEL, DEPLOY ENDPOINT, INFERENCE #################
sw_model = full_fs.to_model(
    model_type=ModelType.CLASSIFIER,
    target_column=target[0],
    feature_list=features,
    name=model_name,
    tags=tags_list,
)
print("Model Creation Complete")

sw_endpoint = sw_model.to_endpoint(name=model_name, tags="nightly", serverless=True)
print(f"Endpoint Deployment Complete")
sw_endpoint = Endpoint(model_name)

# Now run inference on the endpoint
results_df = sw_endpoint.auto_inference(capture=True)
print(f"Endpoint Holdout Inference Ran")
