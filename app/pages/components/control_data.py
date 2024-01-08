import os
from os.path import isfile, join
import re
import pandas as pd
from pandas.testing import assert_index_equal
import mygene
from cmapPy.pandasGEXpress.parse_gct import parse
from cmapPy.pandasGEXpress.write_gct import write

mg = mygene.MyGeneInfo()

def convert_to_ensembleid(gene_symbols: pd.Index):

    query_result = mg.querymany(qterms=gene_symbols, scopes='symbol', fields='symbol,ensembl.gene')
    
    query_result_symbol, query_result_ensembl = zip(*[(item['symbol'],item['ensembl.gene']) 
                                                      for item in query_result])
    
    if ~gene_symbols.equals(pd.Index(query_result_symbol)):
        raise ValueError("Gene ID mapping does not maintain order")
  
    return pd.Index(query_result_ensembl)

def convert_to_symbol(gene_ensembls: pd.Index):
    
    query_result_symbol, query_result_ensembl = zip(*[(item['symbol'],item['ensembl.gene']) 
                                                      for item in mg.querymany(qterms=gene_ensembls, 
                                                                               scopes='ensembl.gene', 
                                                                               fields='symbol,ensembl.gene')
                                                                               ]
                                                                               )
    
    if ~gene_ensembls.equals(pd.Index(query_result_ensembl)):
        raise ValueError("Gene ID mapping does not maintain order")
  
    return pd.Index(query_result_symbol)



class ControlData:
    def __init__(self):
        self.control_data_dir = os.getenv("GTEX_CONTROL_DATA", "GTEx-data/")
        self.control_data = None

    def get_control_data_options(self): 
        return [
            {"label" : ' '.join(re.sub('\.gct$', '', f).split('_')[2:]), "value": f} 
            for f in os.listdir(self.control_data_dir) 
            if isfile(join(self.control_data_dir, f))
        ]

    def get_gene_id(self, column:str, keep_version:bool = True, convert_ensembl_to_symbol:bool = True):
        if column not in ['Name', 'Description']:
            raise ValueError("Wrong column for gene ID")
        
        gene_id = self.control_data[column]

        if ~keep_version:
            # Remove '.<version>' at the end of gene id 
            # The transformation does not happen in place
            gene_id = gene_id.transform(lambda i : re.sub('\.[0-9]+$', '', i)) # Version number should not begin with 0?

        # TODO: convert to symbol

        return gene_id

    def load_control_data(self, filename: str):
        # Get a dataframe from .gct file
        self.control_data = parse(join(self.control_data_dir, filename)).data_df

        gene_id = self.get_gene_id('Description')
        # print(gene_id)
        
        # gene_symbol_id = convert_to_symbol(pd.Index(gene_id))

        # # Is description symbol?
        # if gene_symbol_id.equals(control_data['Description']):
        #     print("Descriptoin is the symbol")

        self.control_data.drop(columns=['Name', 'Description'], inplace=True)

        # Re-index the dataframe using gene id 
        # TODO: will it raise an error if there are duplicates?
        self.control_data.index = gene_id
        
        # Gene ids are not unique
        if gene_id.duplicated().any():
            print("Reduce duplicate IDs ......")
            self.control_data = self.control_data.loc[~self.control_data.index.duplicated(keep='first')]
            # print(gene_id[gene_id.duplicated()])
            # raise ValueError("Duplicate index")



    def filter_control_data(self, genes: pd.Index):
        try:
            # Index rows of genes and transpose to make genes columns
            # TODO: make sure genes in the same order as in user data (done)

            # Genes that control data don't have
            genes_not_exit = genes.difference(self.control_data.index)

            # With this, KeyError should not occurr with .loc
            if ~(genes_not_exit.empty):
                print("Complete genes list: ", len(genes))
                genes = genes.intersection(self.control_data.index)
                print("Genes in intersection: ", len(genes))

            # symbol id as index
            self.control_data = self.control_data.loc[genes].T.astype(float)

            assert_index_equal(self.control_data.columns, genes)

            # if ~self.control_data.columns.equals(genes):
            #     print(self.control_data.columns.difference(genes))
            #     raise ValueError("Unalignable columns of control data")
            
            return genes_not_exit

        # Do not use control data if not every gene in user data exists in the control data set
        except KeyError:
            self.control_data = None
            print("Not every gene in user data exists in the selected control data set")
            return None
    

if __name__ == "__main__":
    gtex_control_data = parse("GTEx-data/gene_tpm_adipose_subcutaneous.gct")

    print(gtex_control_data.row_metadata_df.shape)
    print(gtex_control_data.col_metadata_df.shape)
    print(gtex_control_data.data_df.shape)