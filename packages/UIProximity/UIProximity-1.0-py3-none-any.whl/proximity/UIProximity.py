#!/usr/bin/env python
# coding: utf-8

# In[14]:


'''
Author : Providence Adu, Ph.D
'''

import arcpy 
import os
import pandas as pd


# In[9]:


class Proximity():
    
    '''
    This is class executes proximity analysis for Urban Institute's QOL spatial variables
    '''
    
    def __init__(self, TaxParcelFeatureClass,ProximityFeatureClass):
        
        '''
        The proximity class is initialized with two parameters:. 
        - Tax parcel feature class
        - Input feature class for proximity analysis or
           name of merged proximity feature class
        '''
        
        self.TaxParcelFeatureClass = TaxParcelFeatureClass
        self.ProximityFeatureClass = ProximityFeatureClass

        
        
    def merge(self,*FeatureClassesToBeMerged):
        
        '''
        The merge methods combines proximity feature classes from multiple sources into one 
        feature class for subsequent analysis. If there is only one feature class for the
        proximity analysis, this method will be skipped. The method takes one parameter which 
        can be a string names of two or more feature classes to be merged 
        '''

        self.FeatureClassesToBeMerged = FeatureClassesToBeMerged
        
        print('Converting feature classes  into readble arcpy format')

        inputdata = ';'
        data = inputdata.join(self.FeatureClassesToBeMerged)
        
        print(str(self.FeatureClassesToBeMerged) + " will be merged and named " + self.ProximityFeatureClass)
        
        print('Merging Feature classes')
        
        arcpy.management.Merge(data,self.ProximityFeatureClass, '',"NO_SOURCE_INFO")
        
        print('Done merging')
        
        print('The Feature class has '+ str(arcpy.GetCount_management(self.ProximityFeatureClass).getOutput(0) + ' features'))
        
       
        
    def addfield(self, NewFieldName):
        
        '''
        The addfield method creates a field for the proximity feature class.
        It takes the name of the new field as a parameter. e.g ResNearPark 
        '''
        
        self.NewFieldName = NewFieldName
        
        for row in arcpy.ListFields(self.TaxParcelFeatureClass):
            if row.name == self.NewFieldName:
                arcpy.management.DeleteField(self.TaxParcelFeatureClass, self.NewFieldName)
                print(row.name)
        
        print('Adding a fieldname ' + self.NewFieldName)
        
        arcpy.management.AddField(self.TaxParcelFeatureClass, self.NewFieldName, "DOUBLE", None, None, None,
                          self.NewFieldName, "NULLABLE", "NON_REQUIRED", '')
        
        print('Done adding field name')
        
    def nearanalysis(self):
        
        '''
        The near analysis method computes the distance between the tax parcel and 
        the proximity feature class. Then select and export all residential parcels that are
        near the proximity feature class  
        The method takes no parameter. 
        '''
        
        print('Calculating residential parcel within 0.5 miles of ' + self.ProximityFeatureClass)
        
        arcpy.analysis.Near(self.TaxParcelFeatureClass, self.ProximityFeatureClass, "0.5 Miles",
                            "NO_LOCATION", "NO_ANGLE",  "PLANAR", 
                            "NEAR_FID NEAR_FID;NEAR_DIST NEAR_DIST")
        
        print('Querying residential parcels the where near distance is greater than 0 ')
        
        Whereclause = 'Q_Res = 1 And NEAR_DIST > 0'
        selection = arcpy.SelectLayerByAttribute_management(self.TaxParcelFeatureClass,"SUBSET_SELECTION", Whereclause)
        
        print('Total residential parcels selected: ' + str(arcpy.GetCount_management(selection).getOutput(0)))
        
        print('If near distance is greater than 0 ' + self.NewFieldName + " = 1")
        arcpy.management.CalculateField(selection, self.NewFieldName, 1 , "PYTHON3", '',"DOUBLE")
        
        print('Select all parcels where ' + self.NewFieldName + ' =1')
        
        NearRes =  self.NewFieldName + " = 1"
        NearParcels = arcpy.SelectLayerByAttribute_management(self.TaxParcelFeatureClass,"SUBSET_SELECTION", NearRes)
        print('Total parcels where '+ self.NewFieldName + " = 1 : are " + str(arcpy.GetCount_management(selection).getOutput(0)))
        
        print('Deleting fields added by the near tool')
        
        for row in arcpy.ListFields(self.TaxParcelFeatureClass):
            if row.name in('NEAR_FID','NEAR_DIST'):
                arcpy.management.DeleteField(self.TaxParcelFeatureClass, row.name)
                print(row.name)
                
        return NearParcels
        
    def summarize(self,NearResidentialOutputTable,HousingUnitsTable,Geodatabase):
        
        '''
        The summarize method computes summary of residential units that are in proximity to 
        the proximity feature class. The summarize method takes three parameters:
        1. Output name for summarized residential units in near proximity feature class
        2. Output name for all residential units in the tax parcel database 
        3. The geodatabase where these outputs will be exported to
        
        '''
        
        self.NearResidentialOutputTable = NearResidentialOutputTable
        self.HousingUnitsTable = HousingUnitsTable
        self.Geodatabase = Geodatabase
        self.NearResidentialOutputtJoinTable = NearResidentialOutputTable + "Join"    #Output name for Join table
        self.PercentUnitsFieldName = 'm'  #Name for PercentField
        
        print("Running near analysis and filtering near parcels for summary")
        
        Near_Parcels = self.nearanalysis()
        
        print('Summarizing sum of units that are near residential units')

        arcpy.gapro.SummarizeAttributes(Near_Parcels,self.NearResidentialOutputTable ,"NPA", "units SUM",
                                        None, None, None)
        
        print("Running Q_Res = 1 to query residential parcels")
        
        QResidential =  'Q_Res = 1'

        ResidentialParcels = arcpy.SelectLayerByAttribute_management(self.TaxParcelFeatureClass,"SUBSET_SELECTION", 
                                                             QResidential)
        
        print('Total residential tax parcels are ' + str(arcpy.GetCount_management(ResidentialParcels).getOutput(0)))
        
        print("Summarizing sum of all residential units")
        
        arcpy.gapro.SummarizeAttributes(ResidentialParcels, self.HousingUnitsTable,"NPA", "units SUM",
                                        None, None, None)
        
        print("Selecting parcel and near residential units where NPA is not null, joining them using NPA")
        
        TabNPA = 'NPA IS NOT NULL'
        
        NearUnitsselected = arcpy.management.SelectLayerByAttribute(self.NearResidentialOutputTable, "NEW_SELECTION",
                                                                     TabNPA, None)
        
        ALLUnitsselect = arcpy.management.SelectLayerByAttribute(self.HousingUnitsTable, "NEW_SELECTION",
                                                                 TabNPA, None)
        
        JoinedUnits =  arcpy.management.AddJoin(ALLUnitsselect, "NPA", NearUnitsselected, "NPA", "KEEP_ALL")
        
        print('Exporting joined tables as ' + self.NearResidentialOutputtJoinTable )
        
        arcpy.conversion.TableToTable(JoinedUnits,self.Geodatabase, self.NearResidentialOutputtJoinTable, '', '', '')
        
        print("Adding " + self.PercentUnitsFieldName )
        
        arcpy.management.AddField(self.NearResidentialOutputtJoinTable, self.PercentUnitsFieldName, "DOUBLE", None, None, None,
                          self.PercentUnitsFieldName, "NULLABLE", "NON_REQUIRED", '')
        
        arcpy.management.AddField(self.NearResidentialOutputtJoinTable, 'Year', "TEXT", None, None, None,
                          'Year', "NULLABLE", "NON_REQUIRED", '')
        

        arcpy.management.CalculateField(self.NearResidentialOutputtJoinTable, 'Year', 
                                        '"'+str(self.ProximityFeatureClass[-4:])+'"', 
                                        "PYTHON3", '', "TEXT")
        
        arcpy.AlterField_management(self.NearResidentialOutputtJoinTable, 'SUM_units', 
                                    self.HousingUnitsTable, self.HousingUnitsTable)
        arcpy.AlterField_management(self.NearResidentialOutputtJoinTable, 'SUM_units_1', 
                                    self.NearResidentialOutputTable, self.NearResidentialOutputTable)
        
        print('Calculating percent units that are near proximity feature class')
        
        arcpy.management.CalculateField(self.NearResidentialOutputtJoinTable, self.PercentUnitsFieldName, 
                                        "(!"+self.NearResidentialOutputTable+"!"+"/"+"!"+self.HousingUnitsTable+"!)"+"*100", 
                                        "PYTHON3", '', "TEXT")
        
        arcpy.management.CalculateField(self.NearResidentialOutputtJoinTable, self.HousingUnitsTable, 
                                        "(!"+self.HousingUnitsTable+"!"+"/"+"100)", 
                                        "PYTHON3", '', "TEXT")
        
    
        for row in arcpy.ListFields(self.NearResidentialOutputtJoinTable):
            if row.name in('OID_','COUNT','OBJECTID','NPA_1','COUNT_1'):
                arcpy.management.DeleteField(self.NearResidentialOutputtJoinTable, row.name)
            
        
        return self.NearResidentialOutputtJoinTable
        
    def exportcsv(self,OutputDirectory,FinalCSVName):
        
        '''
        The exportcsv method exports the results on the proximity analysis as csv output
        The method takes two parameters
        1. Output directory where csv file will be exported to 
        2. Name of the csv file
        '''
        
        self.FinalCSVName = FinalCSVName
        self.OutputDirectory = OutputDirectory
        table = self.NearResidentialOutputtJoinTable
        
        fields = arcpy.FieldMappings()
        fields.addTable(table)
    
        
        print("Exporting csv file with the name " + self.FinalCSVName)
        arcpy.conversion.TableToTable(table, self.OutputDirectory, self.FinalCSVName, '', fields, '')
        
        print('Re-reading ' + self.FinalCSVName + ' file')
        
        GIScsvfile = pd.read_csv(self.FinalCSVName)
        
        FinalFile = pd.DataFrame(GIScsvfile[['NPA', self.NearResidentialOutputTable,
                                             self.HousingUnitsTable,self.PercentUnitsFieldName]])
        
        print('Subseting NPA, r, d and m columns')
        
        print('Exporting csv file ')
        
        FinalFile.to_csv(self.FinalCSVName, index = False)
        
        print('Succesfully completed')

