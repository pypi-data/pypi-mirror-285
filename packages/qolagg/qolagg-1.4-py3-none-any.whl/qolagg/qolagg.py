#!/usr/bin/env python
# coding: utf-8

# In[28]:

'''
Author: Providence Adu, Ph.D
'''

import arcpy 
import pandas as pd


# In[21]:


class aggregate():
    
    '''
    This class executes aggregation data for Urban Institute's QOL Variables
    '''
    
    def __init__(self,InFeatureClass):
        '''
        The aggregate class is initialized with Input Featureclass parameters
        '''
        self.InFeatureClass = InFeatureClass
    
    def merge(self,*FeatureClassesToBeMerged):

        '''
        The merge methods combines feature classes from multiple sources into one 
        feature class for subsequent analysis. If there is only one feature class for the
        aggregate analysis, this method will be skipped. The method takes one parameter which 
        can be a string names of two or more feature classes to be merged 
        '''

        self.FeatureClassesToBeMerged = FeatureClassesToBeMerged

        print('Converting feature classes  into readble arcpy format')

        inputdata = ';'
        data = inputdata.join(self.FeatureClassesToBeMerged)

        print(str(self.FeatureClassesToBeMerged) + " will be merged and named " + self.InFeatureClass)
        print('Merging Feature classes')

        arcpy.management.Merge(data,self.InFeatureClass, '',"NO_SOURCE_INFO")

        print('Done merging')

        print('The Feature class has '+ str(arcpy.GetCount_management(self.InFeatureClass).getOutput(0) + ' features'))

    
    def withinNPA(self,NPA,OutputName):
        
        '''
        The withinNPA method aggregates all points feature classess that are completely contained by an NPA
        The with NPA method takes two parameters:
        - Input NPA which is supposed to be a polygon
        - Name of output feature class
        '''
        
        self.NPA = NPA
        self.OutputName = OutputName
        
        print('mapping fields for ' + self.NPA +  ' and ' + self.InFeatureClass)
        
        fields = arcpy.FieldMappings()
        fields.addTable(self.NPA)
        fields.addTable(self.InFeatureClass)
        
        print('Done mapping fields')
        
        print('Executing spatial join for ' + self.NPA +'s ' + 'that completely contains '+ self.InFeatureClass)
        
        arcpy.analysis.SpatialJoin(self.NPA,
                                   self.InFeatureClass,
                                   self.OutputName,
                                  "JOIN_ONE_TO_ONE",
                                   "KEEP_ALL",fields,
                                  "COMPLETELY_CONTAINS",
                                   None, '')
        
        print('Done running spatial join')
        
        print('Renanimg Joint Count as ' + self.OutputName)
        
        arcpy.AlterField_management(self.OutputName, 'Join_Count',self.OutputName,self.OutputName)
        
        return self.OutputName
        
        
    def withNPAID(self,NPA,OutputName):
        
        '''
        The withNPAID methods assigns NPA ID to all point feature classes that are completely with an NPA
        The withNPAID method takes two parameters :
        - Input feature class which is supposed to a point 
        - Name of output feature class 
        '''
        

        self.NPA = NPA
        self.OutputName = OutputName
        
        print('mapping fields for ' + self.InFeature +  ' and ' + self.NPA)
        
        print('Executing spatial join for ' +  self.InFeatureClass + 'that are completely within '+ self.NPA)
        
        fields = arcpy.FieldMappings()
        fields.addTable(self.InFeatureClass)
        fields.addTable(self.NPA)
        
        print('Done running spatial join')
        
        arcpy.analysis.SpatialJoin(self.InFeatureClass,
                                   self.NPA,
                                   self.OutputName,
                                  "JOIN_ONE_TO_ONE",
                                   "KEEP_ALL",fields,
                                  "COMPLETELY_WITHIN",
                                   None, '')
        
        print('Done running spatial join')
        
        print('Renanimg Joint Count as ' + self.OutputName)
        arcpy.AlterField_management(self.OutputName, 'Join_Count',self.OutputName,self.OutputName)
              
        return self.OutputName
        
    def exportcsv(self,OutputDirectory,PopulationFile,PopulationColumn,FileName,):
        
        self.FileName = FileName
        self.OutputDirectory = OutputDirectory
        table = self.OutputName
        self.PopulationYear = PopulationColumn
        self.PopulationFile = PopulationFile
        
        
        fields = arcpy.FieldMappings()
        fields.addTable(self.OutputName)
        
        arcpy.conversion.TableToTable(table, self.OutputDirectory, self.FileName, '', fields, '')
        
        
        print('Re-reading ' + self.FileName + ' file')
        
        GIScsvfile = pd.read_csv(self.FileName)
        
        print('Reading Population Data')
        Popfile = pd.read_csv(self.PopulationFile)
        
        
        print('Joining Population data to NPA variable')
    
        PopFileMerge = pd.merge(GIScsvfile,Popfile,on ='NPA')
        
        PopFileMerge['r'] = PopFileMerge[self.OutputName]
        PopFileMerge['d'] = PopFileMerge[PopulationColumn]/1000
        PopFileMerge['m'] = PopFileMerge['r']/PopFileMerge['d']
        
        print('Subsetting NPA, r,d, and m columns')
        
        FinalFile = pd.DataFrame(PopFileMerge[['NPA','r', 'd','m']])
        
        FinalFile.to_csv(self.FileName , index = False)
        
        
        print('Exporting csv file ')
        

        
        print('Succesfully completed')

        
    
    


# In[ ]:




