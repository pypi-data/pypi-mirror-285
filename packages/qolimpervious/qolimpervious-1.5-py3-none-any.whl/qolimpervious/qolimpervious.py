#!/usr/bin/env python
# coding: utf-8




import arcpy 
import pandas as pd





class impervious():
    '''
    This class executes impervious surface analysis for Urban Institute's QOL Variables
    '''
    def __init__(self, residential, commercial, UnionOutputname):
        
        '''
        The inpervious class is initialized by three parameters:
        - The residential landuse Feature class
        - The commercial landuse Feature class
        - Name of ouput feature class for Union Analysis 
        
        '''
        
        self.residential = residential + " #"
        self.commercial = commercial + " #"
        self.UnionOutputname = UnionOutputname
        self.DissolveOutput = str(residential[:3]) + str(commercial[:3]) + "_dissolve"
        
    def union(self):
        
        '''
        The union method unions the residential and commercial feature classes used for computing
        the total impervious surface in the city. The union method has no parameters as it uses
        the initialized parameters as arguments
        '''
        
        unioned = [self.residential,self.commercial]
        seperator = ';'
        data = seperator.join(unioned)
        
        print('Running union analysis on ' + self.residential[:-1] + ' and ' + self.commercial[:-1] )
        print('The input data for the union is ' + data + " and the ouput is " + self.UnionOutputname)
        
        arcpy.analysis.Union(data,self.UnionOutputname,"ALL", None, "GAPS")
        
        print('Done running Union analysis')
        
        return self.UnionOutputname
        
    def dissovle(self):
        
        '''
        The dissolve method takes no parameters. It does the following:
        
        - It adds a field to the Union feature class
        - It then calculate that field as 0
        - It finally dissolves the Union Feature class using the added field 
        
        '''
        
        for row in arcpy.ListFields(self.UnionOutputname):
            if row.name == 'Dissolve':
                print('Deleting any existing field in the ' + self.UnionOutputname + ' feature class called ' + row.name)
                arcpy.management.DeleteField(self.UnionOutputname, row.name)
                print(row.name)
        
        fieldname = 'Dissolve'
        
        print('Adding a field name called ' + fieldname + ' to the ' + self.UnionOutputname + ' feature class' )
        
        arcpy.management.AddField(self.UnionOutputname,  fieldname, "TEXT", None, None, None,fieldname, "NULLABLE",
                                  "NON_REQUIRED", '')
        
        print('Done adding field')
        
        print('Calculating the added field ' + fieldname + ' as 0')
        
        arcpy.management.CalculateField(self.UnionOutputname, fieldname, "0", "PYTHON3", '', "TEXT")
        
        print('Done calculating field')
        
        print('Dissolving ' + self.UnionOutputname + ' feature class using the ' + fieldname + ' field' )
        
        arcpy.management.Dissolve(self.UnionOutputname,self.DissolveOutput,fieldname, None, "MULTI_PART",
                                  "DISSOLVE_LINES")
        
        print('Done dissolving')
        
    def intersect(self,NPAFeatureclass,IntersectOutput):
        
        '''
        The intersect method takes two arguments 
        - The NPA feature class 
        - The output name for the intersect analysis 
        
        The input for the intesect analyis is the NPA feature class and the Output of the dissolve analysis.
        
        After the intersect analysis has been run:
        
        - A field is added to the output feature class of the intersect analysis
        - Using the field, the geometry of the feature class is computed in Acres 
        - A summary output is created for impervious surface in each NPA
        '''
        
        U = self.union()
        D = self.dissovle()
        
        self.NPAFeatureclass = NPAFeatureclass + " #"
        Dissolve = self.DissolveOutput + " #"
        self.IntersectOutput = IntersectOutput
        self.SummaryOutput = IntersectOutput + "_summary"
  
        intersect = [self.NPAFeatureclass, Dissolve]
        
        seperator = ';'
        inputdata =  seperator.join(intersect)
        
        print('The input for the intersect analysis is ' + inputdata + ' and the ouput is ' + self.IntersectOutput)
        
        print('Running intersect analysis')
        
        arcpy.analysis.Intersect(inputdata, self.IntersectOutput, "ALL", None, "INPUT")
        
        print('Done running intersect analysis')
        
        field = "Area"
        
        print('Adding a field called ' + field + ' to the the ' + self.IntersectOutput + ' featureclass')
        
        arcpy.management.AddField(IntersectOutput,  field, "DOUBLE", None, None, None,
                           field, "NULLABLE", "NON_REQUIRED", '')
        
        print('Done adding field')
        
        print('Calculating Area in acres for ' + self.IntersectOutput + ' feature class')
        
        arcpy.management.CalculateGeometryAttributes(self.IntersectOutput, "Area AREA", '', "ACRES", None, 
                                                     "SAME_AS_INPUT")
        print('Done calculating Area')
        
        print('Summarizing total acreage for each NPA')
        
        arcpy.gapro.SummarizeAttributes(self.IntersectOutput, self.SummaryOutput, "NPA", "Area SUM;LandArea SUM",
                                        None, None, None)
        print('Done summarizing ')
        
        return self.SummaryOutput
    
    def exportcsv(self,OutputDirectory,Filename):
        
        '''
        The exportcsv method exports the results on the impervious surface analysis as csv output
        The method takes two parameters
        1. Output directory where csv file will be exported to 
        2. Name of the csv file
        '''
    
        self.OutputDirectory = OutputDirectory
        self.Filename = Filename
        
        fields = arcpy.FieldMappings()
        fields.addTable(self.SummaryOutput)
        
        print("Exporting csv file with the name " + self.Filename)

        arcpy.conversion.TableToTable(self.SummaryOutput, self.OutputDirectory, self.Filename, '', fields, '')
        
        print('Re-reading ' +  self.Filename + ' file')
        
        GIScsvfile = pd.read_csv(self.Filename)
        
        print('Renaming columns')
        
        GIScsvfile.rename(columns={'SUM_Area': 'r', 'SUM_LandArea': 'd'}, inplace=True)
        
        GIScsvfile['d'] =  GIScsvfile['d']/100
        
        GIScsvfile['m'] =  GIScsvfile['r']/ GIScsvfile['d']
        
        GIScsvfile['Year'] = self.UnionOutputname[-4:]
        
        print('Subseting NPA, Year, r, d and m columns')
        
        FinalFile = pd.DataFrame(GIScsvfile[['NPA','Year','r','d','m']])
        
        print('Exporting csv file ')
        
        FinalFile.to_csv(self.Filename, index = False)
        
        print('Done Exporting')

