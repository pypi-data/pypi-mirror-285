#!/usr/bin/env python
# coding: utf-8

# ### Import libraries

# In[1]:


import pandas as pd
import arcpy


# In[4]:


class voters():
    
    '''
    This class executes voter participation analysis for Urban Institute's QOL Variable
    '''    
        
    def __init__(self,voterparticipation,NPA,SummaryTableName):
        
        '''
        The voter participation class is initialized with three parameters
        - The Geocoded voter participation feature class
        - NPA feature class
        - Name of summary table for voters in each NPA
        '''
        
        self.voterparticipation = voterparticipation
        self.NPA = NPA
        self.SummaryTableName= SummaryTableName
        self.SpatialJoinOutput = self.voterparticipation + "Join"
        
        
    def spatialjoin (self):
        
        '''
        This method executes the spatial join and assigns an NPA to each voter
        '''
        
        print('Running spatial join to assign NPA IDs to Geocoded Voters')
        
        arcpy.analysis.SpatialJoin(self.voterparticipation,self.NPA,self.SpatialJoinOutput,"JOIN_ONE_TO_ONE", 
                                   "KEEP_ALL",'', "WITHIN", None, '')
        
        print('Done assign NPA IDs')
        
        return self.SpatialJoinOutput
    
        
    
    def summary(self,*FieldsToBeSummarized):
        
        '''
        The summarize method computes the summary of all voters within each NPA and the 
        total number of active voters within each NPA. The summary field takes one parameter:
        - The name of the fields to be summarized : active voters field and the 'Join_Count' field
        
        Note: The Join_Count is a hardcoded filed because it is derived from the spatial join analysis
        '''
        
        SpatialJoin = self.spatialjoin()
        
        
        self.FieldsToBeSummarized = list(FieldsToBeSummarized)
        Fields = [row + " SUM" for row in self.FieldsToBeSummarized]
        FinalField = ";".join(Fields)
        
        print('Summarizing the total number of voters within each NPA and the toal number of active voters')
        
        arcpy.gapro.SummarizeAttributes(SpatialJoin, self.SummaryTableName,"NPA",FinalField,
                                        None, None, None)
        
        print('Done Summarizing')
        
        
    def export(self,OutputDirectory,FinalCSVName):
        
        '''
        The export method exports the results on the voters participation analysis as csv output
        The method takes two parameters
        1. Output directory where csv file will be exported to 
        2. Name of the csv file
        
        After the initial output has been exported, the csv file is reread and default fileds are
        rename with r,d for their corresponding fields, afterward, the m field is computed before
        the final file is exported. 
        '''
        
        self.OutputDirectory = OutputDirectory
        self.FinalCSVName = FinalCSVName
        fields = arcpy.FieldMappings()
        fields.addTable(self.SummaryTableName)
        
        print('Exporting the summary table with the name  ' + self.FinalCSVName)
        
        arcpy.conversion.TableToTable(self.SummaryTableName, self.OutputDirectory, self.FinalCSVName, '', fields, '')
        
        print('Done exporting the summary table')
        
        print('Reread the  ' + self.FinalCSVName + " file")
        
        voters = pd.read_csv(self.FinalCSVName)
        
        print('rename '+ self.FieldsToBeSummarized[0] + ' as r' + ' and ' + self.FieldsToBeSummarized[1] + ' as d')
        
        voters.rename(columns = { 'SUM_'+ self.FieldsToBeSummarized[0]:'r', 
                                 'SUM_'+self.FieldsToBeSummarized[1]:'d'}, inplace = True)
        
        print('Done renaming')
        
        print('Divide the d by 100 and compute m by dividing r/d')
        
        voters['d'] = voters['d']/100
        voters['m'] = voters['r']/voters['d']
        
        print('Subset NPA, r, d, and m columns from the DataFrame ')
        
        FinalFile = pd.DataFrame(voters[['NPA','r','d','m']])
        
        print('Export the Final File')
        
        FinalFile.to_csv(self.FinalCSVName,index = False)
        
        print('Successfully completed')

