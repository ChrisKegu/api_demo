from flask import Flask, request, jsonify
import streamlit as st  # You need to import Streamlit here if it's not already done.
import plotly.express as px  # Import Plotly if not already done.
from dataclass.data_class import get_admission_data#, get_cooccuring_wards, get_cooccuring_diseases, formatIndex
from dataclass.data_class import get_cooccuring_wards
from dataclass.data_class import get_cooccuring_beds
from dataclass.data_class import get_visitation_data
app = Flask(__name__)



# @app.route('/api/ward_utilization/<int:year_from>/<int:year_to>', methods=['GET'])
@app.route('/api/ward_utilization/<int:year_from>/<int:year_to>/<int:num_diseases>', methods=['GET'])
def api_ward_utilization(year_from, year_to,num_diseases):
    
    # Call  function with the provided parameters
    admissiondf= get_admission_data(year_from, year_to)
    admissiondf=admissiondf.query(f"Year >= {year_from} and Year <={year_to}")
    admissiondf=admissiondf.drop_duplicates(subset=['AdmissionID','VisitationID','WardName'])
    #get number of disease and concatenate diseases
    admissiondf['NumWards']=admissiondf.groupby('VisitationID')['WardName'].transform('count')
    admissiondf['Wards']=admissiondf.groupby('VisitationID')['WardName'].transform(lambda x: ', '.join(x))
    admissiondf['Beds']=admissiondf.groupby('VisitationID')['BedName'].transform(lambda x: ', '.join(x))
    
     #admissiondf=admissiondf[['AdmissionID','VisitationID','NumWards','Beds','Wards','Year']].sort_values(by='NumWards',ascending=False)
    admissiondf=admissiondf[['NumWards','Beds','Wards','Year']].sort_values(by='NumWards',ascending=False)
        
    admissiondf=admissiondf.query(f"NumWards == {num_diseases}").sort_values(by='Year', ascending=True)
        
    grouped_admission_df=admissiondf.groupby(['Year']).agg({'NumWards':'count'}).reset_index()
        
        
    grouped_admission_df['Year']=grouped_admission_df['Year'].astype(str)
        
    ward_dict = admissiondf.to_dict(orient='records')
    ward_by_year_dict = grouped_admission_df.to_dict(orient='records')
    
    cooccuring_df=get_cooccuring_wards(admissiondf)
      
    bed_pair_df=get_cooccuring_beds(admissiondf,'Beds','ConcBeds')
    
    admissiondf=admissiondf.rename(columns={'NumDiseases':'No. of Diseases','ConcDiseases':'Diseases'})
        #remane columns
    cooccuring_df=cooccuring_df.rename(columns={'DiseasePair':'Disease Pairs','CoOccurrenceCount':'Frequency'})
    
    cooccuring_wards_dict = cooccuring_df.to_dict(orient='records')
    bed_pair_dict=bed_pair_df.to_dict(orient='records')
    combined_data = {
        'ward_dict': ward_dict,
        'ward_by_year_dict': ward_by_year_dict,
        'cooccuring_wards_dict':cooccuring_wards_dict,
        'bed_pair_dict':bed_pair_dict
    }
    return jsonify(combined_data)#,jsonify(data_dict1)


@app.route('/api/visitation/<int:year_from>/<int:year_to>/<int:num_diseases>', methods=['GET'])
def api_visitation(year_from, year_to,num_diseases):
    num_diseases=2
    
    visitation_df=get_visitation_data(year_from,year_to)
    # print(visitation_df.head())
    visitation_df_dict = visitation_df.head(200).to_dict(orient='records')
   
    combined_data = {
        'visitation_df_dict': visitation_df_dict,
        # 'ward_by_year_dict': visitation_df_dict,
        
    }
    return jsonify(combined_data)




if __name__ == '__main__':
    app.run(debug=True)
