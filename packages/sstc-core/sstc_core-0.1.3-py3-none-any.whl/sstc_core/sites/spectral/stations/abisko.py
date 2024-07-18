version = '2024_v0.1'
meta ={
    "acronym": "ANS",
    "name": "Abisko Scientific Research Station",
    "is_active": True,
    "short_name": "Abisko"
}

# Active platforms confirmed 2024
 
platforms ={
    'PhenoCams':{   
        'P-BH-FOR-01':{
            'description': 'Building H Top at ANS. Lars Eklundh custom optical camera.', 
            'legacy_acronym':"ANS-FOR-P01", 
            'status': 'active',
            'platform_key': 'P-BH-FOR-01',
            'ROI': 'Forest in Alpine Montain - Abiskojaure at Abisko National Park',
            'Viewing_Direction': 'West',                         
        }, 
    }, 
    
} 
 

legacy_platforms =  {
    'Phenocams':{ 'P-ROI1-1': {
            'description': 'mobotix',
            'legacy_acronym': "OPH-1", 
            'status': 'active'},
        'P-ROI2-1': {
            'description': 'mobotix', 
            'legacy_acronym':"OPH-2",
            'status': 'active', 
            },
        'P-ROI3-1': {
            'description': 'mobotix', 
            'legacy_acronym':"OPH-3",
            'status': 'active'
            },
        'P-ROI4-1': {
            'description': 'mobotix', 
            'legacy_acronym':"OPH-4",
            'status': 'active'
            },
        'P-ROI5-1': {
            'description': 'mobotix', 
            'legacy_acronym':"OPH-5", 
            'status': 'active'},
        'P-M4_5-1': {
            'description': 'mobotix', 
            'legacy_acronym':"M45P01", 
            'status': 'active'},
        },
        'Fixed_Sensors':{ 
        'FMS-STO-M10-1': {
            'description': 'Stordalen Mire Spectral West',
            'legacy_acronym':"SSW", 
            'status': None,
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': '?Decagon',   
            },
            
        'FMS-STO-M10-2': {
            'description': 'Stordalen Mire Spectral East', 
            'legacy_acronym':"SSE", 
            'status': None,
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': '?Decagon', 
            },

        'FMS-STO-M10-3': {
            'description': 'Stordalen Mire Spectral West_Sky-01, Sky_SWE-ANS-SSW-MIR-F01-01', 
            'legacy_acronym':"SWS01", 
            'status': None,
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': 'Skye', 
            },
        'FMS-STO-M10-4': {
            'description': 'Stordalen Mire Spectral West_Sky-02, Sky_SWE-ANS-SSW-MIR-F01-02_2020', 
            'legacy_acronym':"SWS02", 
            'status': None,
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': 'Skye', 
            },
        'FMS-STO-M10-5': {
            'description': 'Stordalen Mire Spectral East_Decagon_01, Decagon_SWE-ANS-SSE-MIR-F02-01', 
            'legacy_acronym':"SED01", 
            'status': None,
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': 'Decagon', 
            },
        'FMS-STO-M10-6': {
            'description': 'Stordalen Mire Spectral East_Decagon_02, Decagon_SWE-ANS-SSE-MIR-F02-02_2020', 
            'legacy_acronym':"SED02", 
            'status': None,
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': 'Decagon', 
            },
        'FMS-STO-M10-7': {
            'description': 'Stordalen Mire Spectral East_Sky_01, Sky_SWE-ANS-SSE-MIR-F02-01', 
            'legacy_acronym':"SES01", 
            'status': None,
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': 'Skye', 
            },
        'FMS-STO-M10-8': {
            'description': 'Stordalen Mire Spectral East_Sky_02, Sky_SWE-ANS-SSE-MIR-F02-02_2020', 
            'legacy_acronym':"SES02", 
            'status': None,
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': 'Skye', 
            },
        'FMS-STO-M10-9': {
            'description': 'Stordalen Mire Spectral', 
            'legacy_acronym':"SMS", 
            'status': None,
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': '?Decagon', 
            },
                                                                         
    },
    
    'UAV':{
            'P4M': {
            'description': 'Phantom 4 Multispectral', 
            'legacy_acronym':"P4", 
            'status': 'Inactive',
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': 'DJI Phantom 4 Multispectral', 
            },
            'M3M': {
            'description': 'Mavic 3 Multispectral', 
            'legacy_acronym':"M3M", 
            'status': 'Inactive',
            'last_calibration_date': "1900-01-01",
            'ms_center_channels': [],
            'type': 'DJI Mavic 3 Multispectral', 
            },
    } 

    }


locations ={
    'BH-FOR':{
        'name': 'ANS Building H Top. Observatorium and Meteorology building',
        'location_id': 'BH-FOR',
        'legacy_acronym': 'ANS-FOR',
        'platforms':{'PhenoCams':['P-BH-FOR-01'] }  
    } 
} 

tobe_depreciated_locations = {
    'ROI1': {
        "name": "Abisko Scientific Research Station",
        "description": "Phenocam Area 1, P01-ROI1-LG",
        "ecosystems": [],
        "is_active": True,        
        },
    'ROI2':{
        "name": "Abisko Scientific Research Station", 
        "description": "Phenocam Area 2, P01-ROI1-R",
        "ecosystems": [],
        "is_active": True,        
        },
    'ROI3':{
        "name": "Abisko Scientific Research Station", 
        "description": "Phenocam Area 3, P01-ROI1-B",
        "ecosystems": [],
        "is_active": True,        
        },
    'ROI4':{
        "name": "Abisko Scientific Research Station", 
        "description": "Phenocam Area 4, P01-ROI4-B",
        "ecosystems": [],
        "is_active": True,        
        }, 
    'ROI5':{
        "name": "Abisko Scientific Research Station", 
        "description": "Phenocam Area 5, P01-ROI5-P",
        "ecosystems": [],
        "is_active": True,        
        },
    'M4_5':{
        "name": "Abisko Scientific Research Station", 
        "description": "mast 4.5m Phenocam 01, P01 center, M45P01",
        "ecosystems": [],
        "is_active": True,        
        },
    'STO-M10':{
        "name": "Stordalen Mire Spectral West & East", 
        "description": "mast 10m, SSW, SSE, Dry, SWS01, SWS02, SED01, SED02",
        "ecosystems": ['MIR'],
        "is_active": True,        
        },
    'STO-ROI6':{
        "name": "Stordalen Mire Spectral", 
        "description": "Potentially it may be the same as STO-M10, SMS",
        "ecosystems": ['MIR'],
        "is_active": False,        
        },
    'MKA-M10':{
        "name": "Miellejohka", 
        "description": "Mast 10m, Miellejohka2020",
        "ecosystems": ['HEA'],
        "is_active": True,        
        },
    'MKA-AOI1':{
        "name": "Miellejohka", 
        "description": "UAV Aerea Of Interest, Miellejohka2020",
        "ecosystems": ['HEA'],
        "is_active": True,        
        },
    
    'STO-FOR-AOI1':
        {
        "name": "Stordalen Forest", 
        "description": "UAV Stordalen_Forest2020, SUF",
        "ecosystems": ['FOR'],
        "is_active": True,        
        },     
    
    'STO-MIR-AOI0':
        {
        "name": "Stordalen Mire", 
        "description": "UAV abiskoMire2020",
        "ecosystems": ['MIR'],
        "is_active": False,        
        },
             
    'STO-MIR-AOI1':
        {
        "name": "Stordalen Mire Center", 
        "description": "UAV 2024",
        "ecosystems": ['MIR'],
        "is_active": True,        
        }, 
    'STO-MIR-AOI2':
        {
        "name": "Stordalen Mire North", 
        "description": "UAV 2024",
        "ecosystems": ['MIR'],
        "is_active": True,        
        },
    'STO-MIR-AOI3':
        {
        "name": "Stordalen Mire South", 
        "description": "UAV 2024",
        "ecosystems": ['MIR'],
        "is_active": True,        
        }, 
}
              

legacy_locations ={
    
                   0:{
                   "name": "Abisko Scientific Research Station",
                   "acronym": "ANS",
                   "description": "",
                   "ecosystems":[],
                   "is_active": True,                   
               },    
                       
               1:{
                   "name": "Abisko Scientific Research Station",
                   "acronym": "OPH-1",
                   "description": "Phenocam Area 1, P01-ROI1-LG",
                   "ecosystems":[],
                   "is_active": True,
                   
               },
               2:{
                   "name": "Abisko Scientific Research Station",
                   "acronym": "OPH-2",
                   "description": "Phenocam Area 2, P01-ROI2-R",
                   "ecosystems":[],
                   "is_active": True,
               },
               3:{
                   "name": "Abisko Scientific Research Station",
                   "acronym": "OPH-3",
                   "description": "Phenocam Area 3, P01-ROI3-B",
                   "ecosystems":[],
                   "is_active": True,
               },
               4:{
                   "name": "Abisko Scientific Research Station",
                   "acronym": "OPH-4",
                   "description": "Phenocam Area 4, P01-ROI4-LB",
                   "ecosystems":[],
                   "is_active": True,
               5:{
                   "name": "Abisko Scientific Research Station",
                   "acronym": "OPH-5",
                   "description": "Phenocam Area 5, P01-ROI5-P",
                   "ecosystems":[],
                   "is_active": True,
               },               
               6:{
                   "name": "Abisko Scientific Research Station",
                   "acronym": "M45P01",
                   "description": "mast 4.5m Phenocam 01, P01 center",
                   "ecosystems":[],
                   "is_active": True,
               },
               7:{
                   "name": "Stordalen Mire Spectral West",
                   "acronym": "SSW",
                   "description": "",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
               8:{
                   "name": "Stordalen Mire Spectral East",
                   "acronym": "SSE",
                   "description": "",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
               9:{
                   "name": "Stordalen Mire Spectral",
                   "acronym": "SMS",
                   "description": "",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
               10:{
                   "name": "Stordalen Mire Spectral West_Sky-01",
                   "acronym": "SWS01",
                   "description": "Sky_SWE-ANS-SSW-MIR-F01-01",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
               11:{
                   "name": "Stordalen Mire Spectral West_Sky-02",
                   "acronym": "SWS02",
                   "description": "Sky_SWE-ANS-SSW-MIR-F01-02_2020",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
               12:{
                   "name": "Stordalen Mire Spectral East_Decagon_01",
                   "acronym": "SED01",
                   "description": "Decagon_SWE-ANS-SSE-MIR-F02-01",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
               13:{
                   "name": "Stordalen Mire Spectral East_Decagon_02",
                   "acronym": "SED02",
                   "description": "Decagon_SWE-ANS-SSE-MIR-F02-02_2020",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
              14:{
                   "name": "Stordalen Mire Spectral East_Sky_01",
                   "acronym": "SES01",
                   "description": "Sky_SWE-ANS-SSE-MIR-F02-01",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
              15:{
                   "name": "Stordalen Mire Spectral East_Sky_02",
                   "acronym": "SES02",
                   "description": "Sky_SWE-ANS-SSE-MIR-F02-02_2020",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
              
              16:{
                   "name": "Miellejohka",
                   "acronym": "MKA",
                   "description": "UAV Miellejohka2020",
                   "ecosystems":["HEA"],
                   "is_active": True,
               },
                                
              17:{
                   "name": "Stordalen Forest",
                   "acronym": "SUF",
                   "description": "UAV Stordalen_Forest2020",
                   "ecosystems":["FOR"],
                   "is_active": True,
               },
                                
              18:{
                   "name": "Stordalen UAV Mire ",
                   "acronym": "SUM",
                   "description": "UAV abiskoMire2020",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },
              
              19:{
                   "name": "Stordalen Mire North",
                   "acronym": "STO-MIR-North-UAV",
                   "description": "UAV 2024",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },    

              20:{
                   "name": "Stordalen Mire Center",
                   "acronym": "STO-MIR-Center-UAV",
                   "description": "UAV 2024",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },    
    
              21:{
                   "name": "Stordalen Mire South",
                   "acronym": "STO-MIR-South-UAV",
                   "description": "UAV 2024",
                   "ecosystems":["MIR"],
                   "is_active": True,
               },                   
               
               },
               
    
} 
 