import unittest
# import lib02_dataframe as ds
import pandas as pd

class Test_df_value_index(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup data once for all tests in this class
        cls.dict01 = {'A': [1, 2, 3], 'B': [4, 5, 1], 'C': [7, 1, 9]}
        cls.df01_01 = pd.DataFrame(cls.dict01, index=['X', 'Y', 'Z'])
        cls.df01_02 = pd.DataFrame(cls.dict01)


    def test_basic01(self):
        actual = ds.df_value_index(self.df01_01,1)
        expect_dict = {'row_index': ['X', 'Y', 'Z'], 'col_index': ['A', 'C', 'B']}
        expect = pd.DataFrame(expect_dict)
        # Use pandas testing utility to compare actual and expected DataFrames
        pd.testing.assert_frame_equal(actual, expect)
    
    def test_no_index_name(self):
        actual = ds.df_value_index(self.df01_02,1)
        expect_dict = {'row_index': [0, 1,2], 'col_index': ['A', 'C', 'B']}
        expect = pd.DataFrame(expect_dict)
        pd.testing.assert_frame_equal(actual, expect)


def test_custom_sort():
    
    list01 = [['a.<-30', 'b.-30to-20', 'c.-19to-15', 'd.-14to-10', 'e.-9to-5', 'f.-4to-1', 'g.0', 'h.1to5', 'i.6to10', 'j.11to15', 'k.16to20', 'l.21to30', 'm.>30'],['1 Year', '10 Years', '11 Years', '12 Years', '13 Years', '2 Years', '3 Years', '4 Years', '5 Years', '6 Years', '7 Years', '8 Years', '9 Years', 'New'],['0', '0 to 5K', '10K to 15K', '15K to 20K', '20K to 25K', '25K+', '5K to 10K'],['-999.0', '0.0', '1.0', '10.0', '11.0', '12.0', '15.0', '16.0', '17.0', '2.0', '29.0', '3.0', '34.0', '4.0', '46.0', '47.0', '5.0', '6.0', '7.0', '8.0', '9.0'],['0.0', '0.2', '0.4', '0.6', '0.8', '1.0', '1.2', '1.4', '1.6', '1.8', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '2.0', '2.2', '2.4', '2.6', '2.8', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0'],['0.0', '0.2', '0.4', '0.6', '0.8', '1.0', '1.2', '1.4', '1.6', '1.8', '10.0', '10.2', '10.4', '10.6', '10.8', '11.0', '11.2', '11.6', '11.8', '12.8', '13.8', '14.6', '15.0', '2.0', '2.2', '2.4', '2.6', '2.8', '3.0', '3.2', '3.4', '3.6', '3.8', '4.0', '4.2', '4.4', '4.6', '4.8', '5.0', '5.2', '5.4', '5.6', '5.8', '6.0', '6.2', '6.4', '6.6', '6.8', '7.0', '7.2', '7.4', '7.6', '7.8', '8.0', '8.2', '8.4', '8.6', '8.8', '9.0', '9.2', '9.6', '9.8'],['-1', '0', '1', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '2', '3', '4', '5', '6', '7', '8', '9'],['0.0', '1.0', '10.0', '11.0', '12.0', '13.0', '14.0', '18.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0'],['0', '1.0', '1st Year Renewal', '2.0', '3.0', '4.0', '5.0', '6.0', '8.0', 'New Business'],['0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', 'New Business'],['0', '1000000', '10000000', '2000000', '500000', '5000000']]
    
    list02 = ['m.>30', 'b.-30to-20', 'a.<-30', 'l.21to30', 'd.-14to-10', 'j.11to15', 'i.6to10', 'h.1to5', 'e.-9to-5', 'f.-4to-1', 'c.-19to-15', 'g.0', 'k.16to20']
    
    list03 = ['7 Years', '8 Years', '9 Years', '10 Years', '11 Years', '6 Years', '5 Years', '4 Years', '3 Years', '2 Years', '1 Year', 'New']
    
    list04 = ['0', '5K to 10K', '15K to 20K', '10K to 15K', '0 to 5K', '25K+']

    
    variable_name = ["aPol_Diff_aVSe_Band", "aPol_Tenure", "eVeh_MileageBand", "eVeh_NumOfSeat", "eVeh_Si_TotalDamage_Band", "eVeh_Si_TotalDamage_Band_2", "eVeh_VehicleAgeatEffective", "fClm_ClaimCountBand", "fClm_Prior2YrODClaimCount", "fClm_PriorYrODClaimCount", "fDed_Deductibleband"]
    
    begin_with = ['New','New Business','1st Year Renewal']
    end_with = ['Unknown']
    
    for i,lst in enumerate(list01):
        
        # for debugging
        if variable_name[i] in ["fClm_Prior2YrODClaimCount"]:
            print()
        ans = ds.custom_sort(lst, begin_with, end_with)
        print(variable_name[i])
        print(ans)
        print()
        
    ans02 = ds.custom_sort(list02, begin_with, end_with)
    ans03 = ds.custom_sort(list03, begin_with, end_with)
    ans04 = ds.custom_sort(list04, begin_with, end_with)
    print()
    

def test_St_GetNum():
    ex01 = "1st Year Renewal"
    ex02 = "-6 Year"
    ex03 = "25+"
    print(St_GetNum(ex01))
    print(St_GetNum(ex02))
    print(St_GetNum(ex03))



def test_custom_sort():
    
    list01 = [['a.<-30', 'b.-30to-20', 'c.-19to-15', 'd.-14to-10', 'e.-9to-5', 'f.-4to-1', 'g.0', 'h.1to5', 'i.6to10', 'j.11to15', 'k.16to20', 'l.21to30', 'm.>30'],['1 Year', '10 Years', '11 Years', '12 Years', '13 Years', '2 Years', '3 Years', '4 Years', '5 Years', '6 Years', '7 Years', '8 Years', '9 Years', 'New'],['0', '0 to 5K', '10K to 15K', '15K to 20K', '20K to 25K', '25K+', '5K to 10K'],['-999.0', '0.0', '1.0', '10.0', '11.0', '12.0', '15.0', '16.0', '17.0', '2.0', '29.0', '3.0', '34.0', '4.0', '46.0', '47.0', '5.0', '6.0', '7.0', '8.0', '9.0'],['0.0', '0.2', '0.4', '0.6', '0.8', '1.0', '1.2', '1.4', '1.6', '1.8', '10.0', '11.0', '12.0', '13.0', '14.0', '15.0', '2.0', '2.2', '2.4', '2.6', '2.8', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0'],['0.0', '0.2', '0.4', '0.6', '0.8', '1.0', '1.2', '1.4', '1.6', '1.8', '10.0', '10.2', '10.4', '10.6', '10.8', '11.0', '11.2', '11.6', '11.8', '12.8', '13.8', '14.6', '15.0', '2.0', '2.2', '2.4', '2.6', '2.8', '3.0', '3.2', '3.4', '3.6', '3.8', '4.0', '4.2', '4.4', '4.6', '4.8', '5.0', '5.2', '5.4', '5.6', '5.8', '6.0', '6.2', '6.4', '6.6', '6.8', '7.0', '7.2', '7.4', '7.6', '7.8', '8.0', '8.2', '8.4', '8.6', '8.8', '9.0', '9.2', '9.6', '9.8'],['-1', '0', '1', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '2', '3', '4', '5', '6', '7', '8', '9'],['0.0', '1.0', '10.0', '11.0', '12.0', '13.0', '14.0', '18.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0'],['0', '1.0', '1st Year Renewal', '2.0', '3.0', '4.0', '5.0', '6.0', '8.0', 'New Business'],['0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', 'New Business'],['0', '1000000', '10000000', '2000000', '500000', '5000000']]
    
    list02 = ['m.>30', 'b.-30to-20', 'a.<-30', 'l.21to30', 'd.-14to-10', 'j.11to15', 'i.6to10', 'h.1to5', 'e.-9to-5', 'f.-4to-1', 'c.-19to-15', 'g.0', 'k.16to20']
    
    list03 = ['7 Years', '8 Years', '9 Years', '10 Years', '11 Years', '6 Years', '5 Years', '4 Years', '3 Years', '2 Years', '1 Year', 'New']
    
    list04 = ['0', '5K to 10K', '15K to 20K', '10K to 15K', '0 to 5K', '25K+']

    
    variable_name = ["aPol_Diff_aVSe_Band", "aPol_Tenure", "eVeh_MileageBand", "eVeh_NumOfSeat", "eVeh_Si_TotalDamage_Band", "eVeh_Si_TotalDamage_Band_2", "eVeh_VehicleAgeatEffective", "fClm_ClaimCountBand", "fClm_Prior2YrODClaimCount", "fClm_PriorYrODClaimCount", "fDed_Deductibleband"]
    
    begin_with = ['New','New Business','1st Year Renewal']
    end_with = ['Unknown']
    
    for i,lst in enumerate(list01):
        
        # for debugging
        if variable_name[i] in ["fClm_Prior2YrODClaimCount"]:
            print()
        ans = custom_sort(lst, begin_with, end_with)
        print(variable_name[i])
        print(ans)
        print()
        
    ans02 = custom_sort(list02, begin_with, end_with)
    ans03 = custom_sort(list03, begin_with, end_with)
    ans04 = custom_sort(list04, begin_with, end_with)
    print()
    

def test_St_GetNum():
    ex01 = "1st Year Renewal"
    ex02 = "-6 Year"
    ex03 = "25+"
    print(St_GetNum(ex01))
    print(St_GetNum(ex02))
    print(St_GetNum(ex03))

def test_pd_get_col():
    path01 = r"C:\Users\n1603499\OneDrive - Liberty Mutual\Documents\15.02 ARM DS\2023\Project05_VN_MechanicalRefresh\Current Working Files\df_only_in_claim.csv"
    df = pd.read_csv(path01)
    ans01 = ds.pd_get_col(df, contain="Total")


if __name__ == '__main__':
    unittest.main()
