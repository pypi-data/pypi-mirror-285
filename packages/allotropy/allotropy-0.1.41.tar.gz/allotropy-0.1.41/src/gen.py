import json

# sys.path += ["/Users/alejo/allotropy", "/Users/alejo/allotropy/src"]
from allotropy.parser_factory import Vendor
from allotropy.testing.utils import from_file

# file_name = "appbio_quantstudio_designandanalysis_QS1_Standard_Curve_example01.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS3_Relative_Quantification_example02.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS5_Standard_Curve_4Plex_example03.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS6_Standard_Curve_example04.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS6Pro_Standard_Curve_example05.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7_Standard_Curve_example06.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7Pro_Genotyping_example07.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7Pro_Multiplex_example08.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7Pro_PCR_with_Melt_example09.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7Pro_Presence_and_Absence_example10.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7Pro_Relative_Quantification_example11.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7Pro_Relative_Quantification_Biogroup_example12.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7Pro_Relative_Standard_Curve_example13.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7Pro_Standard_Curve_example14.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_QS7Pro_Standard_Curve_TAC_example15.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_OpenArray_GeneExp_example16.xlsx"
# file_name = "appbio_quantstudio_designandanalysis_OpenArray_Genotyping_example17.xlsx"

file_name = "thermo_fisher_qubit4_example_1.csv"

test_filepath = (
    f"../tests/parsers/thermo_fisher_qubit4/testdata/{file_name}"
)
allotrope_dict = from_file(test_filepath, Vendor.THERMO_FISHER_QUBIT4)

print(json.dumps(allotrope_dict, indent=4, ensure_ascii=False))  # noqa: T201
