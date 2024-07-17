# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 10:36:59 2024

@author: wolters
"""

import os
from os import access, R_OK
from os.path import isfile

import sys

import re

import logging

import pandas as pd

import numpy as np

import networkx as nx    

import importlib
import glob

import math

import pickle

import geopandas

from datetime import datetime




# ---
# --- PT3S Imports
# ---
logger = logging.getLogger('PT3S')  
if __name__ == "__main__":
    logger.debug("{0:s}{1:s}".format('in MODULEFILE: __main__ Context:','.')) 
else:
    logger.debug("{0:s}{1:s}{2:s}{3:s}".format('in MODULEFILE: Not __main__ Context: ','__name__: ',__name__," .")) 

try:
    from PT3S import Dx
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Dx - trying import Dx instead ... maybe pip install -e . is active ...')) 
    import Dx

try:
    from PT3S import Mx
except ImportError:
    logger.debug("{0:s}{1:s}".format('ImportError: ','from PT3S import Mx - trying import Mx instead ... maybe pip install -e . is active ...')) 
    import Mx

try:
    from PT3S import dxDecodeObjsData
except:
    import dxDecodeObjsData


class dxWithMxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class dxWithMx():
    """Wrapper for dx with attached mx.
    """
    def __init__(self,dx,mx,crs=None):
        
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
            self.dx = dx
            self.mx = mx
            
            self.dfLAYR=dxDecodeObjsData.Layr(self.dx)
            self.dfWBLZ=dxDecodeObjsData.Wblz(self.dx)
            self.dfAGSN=dxDecodeObjsData.Agsn(self.dx)            
                        
            self.V3_ROHR=dx.dataFrames['V3_ROHR']
            self.V3_KNOT=dx.dataFrames['V3_KNOT']
            self.V3_FWVB=dx.dataFrames['V3_FWVB']
            self.V3_VBEL=dx.dataFrames['V3_VBEL']
                                                            
            if isinstance(self.mx,Mx.Mx):  
                
                modellName, ext = os.path.splitext(self.dx.dbFile)
                logger.info("{0:s}{1:s}: processing dx and mx ...".format(logStr,os.path.basename(modellName)))                 
                
                # mx2Idx to V3_KNOT, V3_ROHR, V3_FWVB, etc.
                # mx2NofPts to V3_ROHR  
                # mx2Idx to V3_VBEL
                self.dx.MxSync(self.mx)
                self.V3_ROHR=dx.dataFrames['V3_ROHR']
                self.V3_KNOT=dx.dataFrames['V3_KNOT']
                self.V3_FWVB=dx.dataFrames['V3_FWVB']    
                self.V3_VBEL=dx.dataFrames['V3_VBEL'] 
                                
                # Vec-Results to V3_KNOT, V3_ROHR, V3_FWVB, etc.
                V3sErg=self.dx.MxAdd(mx)                
                self.V3_ROHR=V3sErg['V3_ROHR']
                self.V3_KNOT=V3sErg['V3_KNOT']
                self.V3_FWVB=V3sErg['V3_FWVB']
                
                # ROHR 
                                
                try:                                    
                    t0=pd.Timestamp(self.mx.df.index[0].strftime('%Y-%m-%d %X.%f'))
                    QMAV=('STAT'
                                ,'ROHR~*~*~*~QMAV'
                                ,t0
                                ,t0
                                )
                    self.V3_ROHR['QMAVAbs']=self.V3_ROHR.apply(lambda row: math.fabs(row[QMAV]) ,axis=1)      
                    logger.debug("{0:s}{1:s}".format(logStr,"Constructing of V3_ROHR['QMAVAbs'] ok so far."))                                                      
                except Exception as e:
                    logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                    logger.debug(logStrTmp) 
                    logger.debug("{0:s}{1:s}".format(logStr,'Constructing col QMAVAbs=Abs(STAT ROHR~*~*~*~QMAV) in V3_ROHR failed.'))   
                    
                try:                                                        
                    VAV=('STAT'
                                ,'ROHR~*~*~*~VAV'
                                ,t0
                                ,t0
                                )
                    self.V3_ROHR['VAVAbs']=self.V3_ROHR.apply(lambda row: math.fabs(row[VAV]) ,axis=1)       
                    logger.debug("{0:s}{1:s}".format(logStr,"Constructing of V3_ROHR['VAVAbs'] ok so far."))                                                         
                except Exception as e:
                    logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                    logger.debug(logStrTmp) 
                    logger.debug("{0:s}{1:s}".format(logStr,'Constructing col VAVAbs=Abs(STAT ROHR~*~*~*~VAV) in V3_ROHR failed.'))       
                    
                try:                                                        
                    PHR=('STAT'
                                ,'ROHR~*~*~*~PHR'
                                ,t0
                                ,t0
                                )
                    self.V3_ROHR['PHRAbs']=self.V3_ROHR.apply(lambda row: math.fabs(row[PHR]) ,axis=1)     
                    logger.debug("{0:s}{1:s}".format(logStr,"Constructing of V3_ROHR['PHRAbs'] ok so far."))                                                           
                except Exception as e:
                    logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                    logger.debug(logStrTmp) 
                    logger.debug("{0:s}{1:s}".format(logStr,'Constructing col PHRAbs=Abs(STAT ROHR~*~*~*~PHR) in V3_ROHR failed.'))     

                try:                                                        
                    JV=('STAT'
                                ,'ROHR~*~*~*~JV'
                                ,t0
                                ,t0
                                )
                    self.V3_ROHR['JVAbs']=self.V3_ROHR.apply(lambda row: math.fabs(row[JV]) ,axis=1)      
                    logger.debug("{0:s}{1:s}".format(logStr,"Constructing of V3_ROHR['JVAbs'] ok so far."))                                                          
                except Exception as e:
                    logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                    logger.debug(logStrTmp) 
                    logger.debug("{0:s}{1:s}".format(logStr,'Constructing col JVAbs=Abs(STAT ROHR~*~*~*~JV) in V3_ROHR failed.'))                              
                                        
                # FWVB  
                try:                                                         
                     W=('STAT'
                                 ,'FWVB~*~*~*~W'
                                 ,t0
                                 ,t0
                                 )
                     self.V3_FWVB['W']=self.V3_FWVB[W]
                     logger.debug("{0:s}{1:s}".format(logStr,"Constructing of V3_FWVB['W'] ok so far."))                                                      
                except Exception as e:
                     logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                     logger.debug(logStrTmp) 
                     logger.debug("{0:s}{1:s}".format(logStr,'Constructing col W in V3_FWVB failed.'))   
                     
                try:                                             
                     QM=('STAT'
                                 ,'FWVB~*~*~*~QM'
                                 ,t0
                                 ,t0
                                 )
                     self.V3_FWVB['QM']=self.V3_FWVB[QM]
                     logger.debug("{0:s}{1:s}".format(logStr,"Constructing of V3_FWVB['QM'] ok so far."))                                                      
                except Exception as e:
                     logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                     logger.debug(logStrTmp) 
                     logger.debug("{0:s}{1:s}".format(logStr,'Constructing col QM in V3_FWVB failed.'))     
                     
                try:     
                     TI=('STAT'
                                 ,'FWVB~*~*~*~TI'
                                 ,t0
                                 ,t0
                                 )
                     self.V3_FWVB['TI']=self.V3_FWVB[TI]
                     logger.debug("{0:s}{1:s}".format(logStr,"Constructing of V3_FWVB['TI'] ok so far."))                                                      
                except Exception as e:
                     logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                     logger.debug(logStrTmp) 
                     logger.debug("{0:s}{1:s}".format(logStr,'Constructing col TI in V3_FWVB failed.'))    

                try:     
                     TK=('STAT'
                                 ,'FWVB~*~*~*~TK'
                                 ,t0
                                 ,t0
                                 )
                     self.V3_FWVB['TK']=self.V3_FWVB[TK]
                     logger.debug("{0:s}{1:s}".format(logStr,"Constructing of V3_FWVB['TK'] ok so far."))                                                      
                except Exception as e:
                     logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                     logger.debug(logStrTmp) 
                     logger.debug("{0:s}{1:s}".format(logStr,'Constructing col TK in V3_FWVB failed.'))    
                     
                
                # WBLZ
                
                try:                
                    V_WBLZ=self.dx.dataFrames['V_WBLZ']
                    df=V_WBLZ[['pk','fkDE','rk','tk','BESCHREIBUNG','NAME','TYP','AKTIV','IDIM']]
                    dfMx=mx.getVecAggsResultsForObjectType(Sir3sVecIDReExp='^WBLZ~\*~\*~\*~')
                    if dfMx.empty:
                        logger.debug("{0:s}{1:s}".format(logStr,'Adding MX-Results to V3_WBLZ: no such results.'))           
                    else:
                        dfMx.columns=dfMx.columns.to_flat_index()                    
                        self.V3_WBLZ=pd.merge(df,dfMx,left_on='tk',right_index=True)
                        logger.debug("{0:s}{1:s}".format(logStr,'Adding MX-Results to V3_WBLZ ok so far.'))                 
                except Exception as e:
                    logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                    logger.debug(logStrTmp) 
                    logger.debug("{0:s}{1:s}".format(logStr,'Constructing V3_WBLZ failed.'))
                
                #gdfs
                
                if not crs:
                    try:               
                        dfSG=dx.dataFrames['SIRGRAF']
                        if 'SRID2' in dfSG.columns and dfSG['SRID2'].iloc[1] is not None:
                            crs = 'EPSG:' + str(int(dfSG['SRID2'].iloc[1]))
                        else:
                            crs = 'EPSG:' + str(int(dfSG['SRID'].iloc[1]))
                        logger.debug("{0:s}{1:s} {2:s}".format(logStr, 'crs reading successful: ', crs))
                    except:
                        logger.debug("{0:s}{1:s}".format(logStr,'crs reading error'))  
                else:
                    logger.debug("{0:s}{1:s} {2:s}".format(logStr, 'crs give value used: ', crs))
                
                try:
                    gs=geopandas.GeoSeries.from_wkb(self.V3_FWVB['GEOMWKB'],crs=crs)
                    self.gdf_FWVB=geopandas.GeoDataFrame(self.V3_FWVB,geometry=gs,crs=crs)
                
                    gs=geopandas.GeoSeries.from_wkb(self.V3_ROHR['GEOMWKB'],crs=crs)
                    self.gdf_ROHR=geopandas.GeoDataFrame(self.V3_ROHR,geometry=gs,crs=crs)
                    
                    gs=geopandas.GeoSeries.from_wkb(self.V3_KNOT['GEOMWKB'],crs=crs)
                    self.gdf_KNOT=geopandas.GeoDataFrame(self.V3_KNOT,geometry=gs,crs=crs)
                    
                    logger.debug("{0:s}{1:s}".format(logStr,"Constructing of gdf_FWVB and gdf_ROHR ok so far."))  
                except Exception as e:
                    logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                    logger.debug(logStrTmp) 
                    logger.debug("{0:s}{1:s}".format(logStr,'Constructing gdf_FWVB and gdf_ROHR failed.'))

            # G    
                                
            try:
                # Graph bauen    
                self.G=nx.from_pandas_edgelist(df=self.dx.dataFrames['V3_VBEL'].reset_index(), source='NAME_i', target='NAME_k', edge_attr=True) 
                nodeDct=self.V3_KNOT.to_dict(orient='index')    
                nodeDctNx={value['NAME']:value|{'idx':key} for key,value in nodeDct.items()}
                nx.set_node_attributes(self.G,nodeDctNx)     
                logger.debug("{0:s}{1:s}".format(logStr,'Constructing NetworkX Graph G ok so far.'))                           
                
            except Exception as e:
                logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.debug(logStrTmp) 
                logger.info("{0:s}{1:s}".format(logStr,'Constructing NetworkX Graph G failed.')) 


            try:               
                # Darstellungskoordinaten des Netzes bezogen auf untere linke Ecke == 0,0
                vKnot=self.dx.dataFrames['V3_KNOT']            
                vKnotNet=vKnot[    
                (vKnot['ID_CONT']==vKnot['IDPARENT_CONT'])
                ]
                xMin=vKnotNet['XKOR'].min()
                yMin=vKnotNet['YKOR'].min()            
                self.nodeposDctNx={name:(x-xMin
                              ,y-yMin)
                               for name,x,y in zip(vKnotNet['NAME']
                                                  ,vKnotNet['XKOR']
                                                  ,vKnotNet['YKOR']
                                                  )
                }
                logger.debug("{0:s}{1:s}".format(logStr,'Constructing NetworkX Graph G nodeposDctNx ok so far.'))    
            except Exception as e:
                logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.debug(logStrTmp) 
                logger.info("{0:s}{1:s}".format(logStr,'Constructing NetworkX Graph G nodeposDctNx failed.')) 
               
            # GSig
                             
            try:
                # Graph Signalmodell bauen
                self.GSig=nx.from_pandas_edgelist(df=self.dx.dataFrames['V3_RVBEL'].reset_index(), source='Kn_i', target='Kn_k', edge_attr=True,create_using=nx.DiGraph())
                nodeDct=self.dx.dataFrames['V3_RKNOT'].to_dict(orient='index')
                nodeDctNx={value['Kn']:value|{'idx':key} for key,value in nodeDct.items()}
                nx.set_node_attributes(self.GSig,nodeDctNx)
                logger.debug("{0:s}{1:s}".format(logStr,'Constructing NetworkX Graph GSig ok so far.'))    
            except Exception as e:
                logStrTmp="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
                logger.debug(logStrTmp) 
                logger.info("{0:s}{1:s}".format(logStr,'Constructing NetworkX Graph GSig failed.'))             
      
        except dxWithMxError:
            raise            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise dxWithMxError(logStrFinal)                       
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))            


    def setLayerContentTo(self,layerName,df):
        """
        Updates layerName to df's-Content. df's cols TYPE and ID are used.               
        """        
                
        logStr = "{0:s}.{1:s}: ".format(self.__class__.__name__, sys._getframe().f_code.co_name)
        logger.debug("{0:s}{1:s}".format(logStr,'Start.')) 
        
        try: 
                  
           xk=self.dfLAYR[self.dfLAYR['NAME'].isin([layerName])]['tk'].iloc[0]
            
           dfUpd=df.copy(deep=True)
            
           dfUpd['table']='LAYR'
           dfUpd['attrib']='OBJS'
           dfUpd['attribValue']=dfUpd.apply(lambda row: "{:s}~{:s}\t".format(row['TYPE'],row['ID']).encode('utf-8'),axis=1)
           dfUpd['xk']='tk'
           dfUpd['xkValue']=xk    
            
           dfUpd2=dfUpd.groupby(by=['xkValue']).agg({'xkValue': 'first'
                                               ,'table': 'first'
                                               ,'attrib': 'first'
                                               ,'xk': 'first'
                                               , 'attribValue': 'sum'}).reset_index(drop=True)
           dfUpd2['attribValue']=dfUpd2['attribValue'].apply(lambda x: x.rstrip())
              
           self.dx.update(dfUpd2)               
        
        except dxWithMxError:
            raise            
        except Exception as e:
            logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
            logger.error(logStrFinal) 
            raise dxWithMxError(logStrFinal)                       
        finally:
            logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))            
        
class readDxAndMxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class readDxAndMxGoto(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def readDxAndMx(dbFile            
                ,preventPklDump=False
                ,forceSir3sRead=False
                ,maxRecords=None
                ,mxsVecsResults2MxDf=None
                ,mxsVecsResults2MxDfVecAggs=None
                ,crs=None
                ,logPathOutputFct=os.path.relpath
                ):

    """
    Reads SIR 3S model and SIR 3S results and returns a dxWithMx object.
    
    Use maxRecords=0 to read only the model.
    Use maxRecords=1 to read only STAT (the steady state result).

    :param dbFile: Path to SIR 3S' database file ('modell.db3' or 'modell.mdb'). The database is read into a Dx object. The corresponding results are read into an Mx object if available.
    :type dbFile: str
    :param preventPklDump: Determines whether to prevent dumping objects read to pickle. If True, existing pickles are deleted, SIR 3S' sources are read and no pickles are written. If False 3 pickles are written or overwritten if older than SIR 3S' sources.
    :type preventPklDump: bool, optional, default=False
    :param forceSir3sRead: Determines whether to force reading from SIR 3S' sources even if newer pickles exists. By default pickles are read if newer than SIR 3S' sources.
    :type forceSir3sRead: bool, optional, default=False
    :param maxRecords: Use maxRecords=0 to read only the model. Use maxRecords=1 to read only STAT (the steady state result). Maximum number of MX-Results to read. If None, all results are read.
    :type maxRecords: int, optional, default=None
    :param mxsVecsResults2MxDf: List of regular expressions for SIR 3S' Vector-Results to be included in mx.df. Note that integrating Vector-Results in mx.df can significantly increase memory usage. Example: ['ROHR~\*~\*~\*~PHR', 'ROHR~\*~\*~\*~FS', 'ROHR~\*~\*~\*~DSI', 'ROHR~\*~\*~\*~DSK']
    :type mxsVecsResults2MxDf: list, optional, default=None
    :param mxsVecsResults2MxDfVecAggs: List of timesteps for SIR 3S' Vector-Results to be included in mx.dfVecAggs. Note that integrating all timesteps in mx.dfVecAggs will increase memory usage up to MXS-Size. Example: [3,42,666]
    :type mxsVecsResults2MxDfVecAggs: list, optional, default=None
    :param crs: (=coordinate reference system) Determines crs used in geopandas-Dfs (Possible value:'EPSG:25832'). If None, crs will be read from SIR 3S' database file.
    :type crs: str, optional, default=None
    :param logPathOutputFct: logPathOutputFct(fileName) is used for logoutput of filenames unless explicitly stated otherwise in the logoutput
    :type logPathOutputFct: function, optional

    :return: An object containing the SIR 3S model and SIR 3S results.
    :rtype: dxWithMx

    .. note:: Dx contains data for all models in the SIR 3S database. Mx contains only the results for one model. SYSTEMKONFIG / VIEW_MODELLE are used to determine which one.
        
        The returned dxWithMx object has the following structure i.e. Dfs:
    
            - Model: Dx object:
                - dx.dataFrames[...]: pandas-Dfs 1:1 from SIR 3S' tables in database file
                - Dfs derived from SIR 3S' tables above:
                    - V3_VBEL: edge data
                    - V3_KNOT: node data
                    - NetworkX Example:
                        - vVbel=self.dataFrames['V3_VBEL'].reset_index()
                        - G=nx.from_pandas_edgelist(df=vVbel, source='NAME_i', target='NAME_k', edge_attr=True) 
                        - vKnot=self.dataFrames['V3_KNOT']
                        - nodeDct=vKnot.to_dict(orient='index')
                        - nodeDctNx={value['NAME']:value|{'idx':key} for key,value in nodeDct.items()}
                        - nx.set_node_attributes(G,nodeDctNx)                
    
            - Results: Mx object:
                - mx.df: pandas-Df ('time curve data') from from SIR 3S' MXS file(s)
                - mx.dfVecAggs: pandas-Df ('vector data') from SIR 3S' MXS file(s)
    
            - pandas-Dfs with Model- and Result-data:
                - V3_ROHR: Pipes
                - V3_FWVB: Housestations District Heating
                - V3_KNOT: Nodes 
    
            - geopandas-Dfs based upon the Dfs above:
                - gdf_ROHR: Pipes
                - gdf_FWVB: Housestations District Heating
                - gdf_KNOT: Nodes 
                    
            - Dfs containing decoded BLOB-Data:
                - dfLAYR: one row per LAYR (Layer) and OBJ
                - dfWBLZ: one row per WBLZ (Heat balance) and OBJ
                - dfAGSN: one row for AGSN and OBJ (edge); AGSN is the German abbreviation for longitudinal sections / cuts (defined in the SIR 3S model)

        The returned dxWithMx object has almost no functions yet - except:
                - setLayerContentTo(layerName,df): cols TYPE and ID are used in df to set the content of LAYR layerName in the SIR 3S database to df
             

    """
    
    import os
    #import importlib
    import glob
    
    dx=None
    mx=None
    
    logStr = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}{1:s}".format(logStr,'Start.'))     
    
    try:
        
        dx=None
        mx=None
        m=None
            
        dbFileDxPklRead=False
        dbFilename,ext=os.path.splitext(dbFile)
        dbFileDxPkl="{:s}-dx.pkl".format(dbFilename)   
        
        if preventPklDump:
            if isfile(dbFileDxPkl):
              logger.info("{logStr:s}{dbFileDxPkl:s} exists and is deleted...".format(
                   logStr=logStr
                  ,dbFileDxPkl=logPathOutputFct(dbFileDxPkl)                        
                  )
                  )
              os.remove(dbFileDxPkl)           
                
        if not forceSir3sRead:            
            # Pkl existiert
            if os.path.exists(dbFileDxPkl):                
                # ist eine Datei und lesbar
                if isfile(dbFileDxPkl) and access(dbFileDxPkl,R_OK):
                    # ist neuer als die Modelldatenbank
                    tDb=os.path.getmtime(dbFile)
                    tPkl=os.path.getmtime(dbFileDxPkl)
                    
                    logger.debug("{:s} tDb: {:s} tPkl: {:s}".format(logStr
                                                                      ,datetime.fromtimestamp(tDb).strftime('%Y-%m-%d %H:%M:%S')
                                                                      ,datetime.fromtimestamp(tPkl).strftime('%Y-%m-%d %H:%M:%S')                                                                      
                                                                      ))    
                    
                    if tDb < tPkl:
                        logger.info("{logStr:s}{dbFileDxPkl:s} newer than {dbFile:s} and therefore read ...".format(
                             logStr=logStr
                            ,dbFileDxPkl=logPathOutputFct(dbFileDxPkl)
                            ,dbFile=logPathOutputFct(dbFile)
                            )
                            )
                        try:
                            with open(dbFileDxPkl,'rb') as f:  
                                dx=pickle.load(f)  
                            dbFileDxPklRead=True
                        except:                            
                            logger.info("{logStr:s}{dbFileDxPkl:s} read error! - reading SIR 3S raw data ...".format(
                                 logStr=logStr
                                ,dbFileDxPkl=logPathOutputFct(dbFileDxPkl)                                
                                )
                                )

        ### Modell lesen
        if not dbFileDxPklRead:
            try:
                dx=Dx.Dx(dbFile)
            except Dx.DxError:
                logStrFinal="{logStr:s}dbFile: {dbFile:s}: DxError!".format(
                    logStr=logStr
                    ,dbFile=logPathOutputFct(dbFile)
                    )     
                raise readDxAndMxError(logStrFinal)  
            
            if not preventPklDump:
                if isfile(dbFileDxPkl):
                    logger.info("{logStr:s}{dbFileDxPkl:s} exists and is overwritten...".format(
                         logStr=logStr
                        ,dbFileDxPkl=logPathOutputFct(dbFileDxPkl)                        
                        )
                        )
                else:
                    logger.info("{logStr:s}{dbFileDxPkl:s} is written ...".format(
                         logStr=logStr
                        ,dbFileDxPkl=logPathOutputFct(dbFileDxPkl)                        
                        )
                        )                                                                
                with open(dbFileDxPkl,'wb') as f:  
                    pickle.dump(dx,f)           
                    
            else:
                pass
                                                               
        ### Ergebnisse nicht lesen?!         
        if maxRecords==0:        
            m = dxWithMx(dx,None,crs)
            logStrFinal="{logStr:s}dbFile: {dbFile:s}: maxRecords==0: do not read MX-Results.".format(
                logStr=logStr
                ,dbFile=logPathOutputFct(dbFile))     
            raise readDxAndMxGoto(logStrFinal)               
                             
        ### mx Datenquelle bestimmen
        logger.debug("{logStrPrefix:s}dx.dbFile literally: {dbFile:s}".format(
            logStrPrefix=logStr
           ,dbFile=dx.dbFile))
        #!
        dbFile=os.path.abspath(dx.dbFile)
        logger.debug("{logStrPrefix:s}abspath of dx.dbFile: {dbFile:s}".format(
            logStrPrefix=logStr
            ,dbFile=dbFile))

        # wDir der Db
        sk=dx.dataFrames['SYSTEMKONFIG']
        wDirDb=sk[sk['ID'].isin([1,1.])]['WERT'].iloc[0]
        logger.debug("{logStrPrefix:s} wDir from dbFile: {wDirDb:s}".format(
            logStrPrefix=logStr,wDirDb=wDirDb))
        #!
        wDir=os.path.abspath(os.path.join(os.path.dirname(dbFile),wDirDb))
        logger.debug("{logStrPrefix:s} abspath of wDir from dbFile: {wDir:s}".format(
            logStrPrefix=logStr,wDir=wDir))

        # SYSTEMKONFIG ID 3:
        # Modell-Pk des in QGIS anzuzeigenden Modells (wird von den QGIS-Views ausgewertet)
        # diese xk wird hier verwendet um das Modell in der DB zu identifizieren dessen Ergebnisse geliefert werden sollen
        try:
            vm=dx.dataFrames['VIEW_MODELLE']
            modelXk=sk[sk['ID'].isin([3,3.])]['WERT'].iloc[0]
            vms=vm[vm['pk'].isin([modelXk])].iloc[0]   
        except:
            logger.debug("{logStr:s} SYSTEMKONFIG ID 3 not defined. Value (ID==3) is supposed to define the Model which results are expected in mx. Now the 1st Model in VIEW_MODELLE is used...".format(logStr=logStr))
            vms=vm.iloc[0]  
        
        #!                        
        wDirMx=os.path.join(
            os.path.join(
            os.path.join(wDir,vms.Basis),vms.Variante),vms.BZ)
        logger.debug("{logStrPrefix:s}wDirMx from abspath of wDir from dbFile: {wDirMx:s}".format(
            logStrPrefix=logStr,wDirMx=wDirMx))
                        
        wDirMxMx1Content=glob.glob(os.path.join(wDirMx,'*.MX1'))
        wDirMxMx1Content=sorted(wDirMxMx1Content) 

        if len(wDirMxMx1Content)>1:
            logger.debug("{logStrPrefix:s}Mehr als 1 ({anz:d}) MX1 in wDirMx vorhanden.".format(
                logStrPrefix=logStr,anz=len(wDirMxMx1Content)))
        mx1File= wDirMxMx1Content[0]
        logger.debug("{logStrPrefix:s}mx1File: {mx1File:s}".format(
            logStrPrefix=logStr
            ,mx1File=logPathOutputFct(mx1File)))
        
        
        dbFileMxPklRead=False
        dbFileMxPkl="{:s}-mx-{:s}.pkl".format(dbFilename,re.sub('\W+','_',os.path.relpath(mx1File)))                
        logger.debug("{logStrPrefix:s}zugeh. dbFileMxPkl-File: {dbFileMxPkl:s}".format(
            logStrPrefix=logStr
            ,dbFileMxPkl=logPathOutputFct(dbFileMxPkl)))
        
        if preventPklDump:
            if isfile(dbFileMxPkl):
                  logger.info("{logStr:s}{dbFileMxPkl:s} exists and is deleted...".format(
                       logStr=logStr
                      ,dbFileMxPkl=logPathOutputFct(dbFileMxPkl)                        
                      )
                      )
                  os.remove(dbFileMxPkl)        
                       
        tDb=os.path.getmtime(dbFile)  
        if os.path.exists(mx1File):  
            tMx=os.path.getmtime(mx1File)
            if tDb>tMx:
                logger.info("{logStr:s}{dbFile:s} is newer than {mx1File:s}: SIR 3S' dbFile is newer than SIR 3S' mxFile; in this case the results are maybe dated or (worse) incompatible to the model".format(
                     logStr=logStr                    
                    ,mx1File=logPathOutputFct(mx1File)
                    ,dbFile=logPathOutputFct(dbFile)
                    )
                    )   
                wDirMxXmlContent=glob.glob(os.path.join(wDirMx,'*.XML'))
                wDirMxXmlContent=sorted(wDirMxXmlContent) 
                xmlFile= wDirMxXmlContent[0]
                tXml=os.path.getmtime(xmlFile)
                if tMx>=tXml:
                    pass
                else:
                    pass
                    logger.info("{logStr:s}{xmlFile:s} is newer than {mx1File:s}: SirCalc's xmlFile is newer than SIR 3S' mxFile; in this case the results are dated or (worse) incompatible to the model".format(
                         logStr=logStr                    
                        ,xmlFile=logPathOutputFct(xmlFile)
                        ,mx1File=logPathOutputFct(mx1File)
                        )
                        )   
        else:
             m = dxWithMx(dx,None,crs)
             logStrFinal="{logStr:s}dbFile: {dbFile:s} no {mx1File:s}.".format(
                 logStr=logStr
                 ,mx1File=logPathOutputFct(mx1File)
                 ,dbFile=logPathOutputFct(dbFile)
                 )     
             raise readDxAndMxGoto(logStrFinal)             
                                        
        if not forceSir3sRead:            
            # Pkl existiert
            if os.path.exists(dbFileMxPkl):                
                # ist eine Datei und lesbar
                if isfile(dbFileMxPkl) and access(dbFileMxPkl,R_OK):
                    # ist neuer als mx1File
                    tMx=os.path.getmtime(mx1File)
                    tPkl=os.path.getmtime(dbFileMxPkl)                    
                                        
                    logger.debug("{:s} tMx: {:s} tPkl: {:s}".format(logStr
                                                  ,datetime.fromtimestamp(tMx).strftime('%Y-%m-%d %H:%M:%S')
                                                  ,datetime.fromtimestamp(tPkl).strftime('%Y-%m-%d %H:%M:%S')                                                                      
                                                  ))                        
                                        
                    if tMx < tPkl:
                        logger.info("{logStr:s}{dbFileMxPkl:s} newer than {mx1File:s} and therefore read ...".format(
                             logStr=logStr
                            ,dbFileMxPkl=logPathOutputFct(dbFileMxPkl)
                            ,mx1File=logPathOutputFct(mx1File)
                            )
                            )
                        try:
                            with open(dbFileMxPkl,'rb') as f:  
                                mx=pickle.load(f)  
                            dbFileMxPklRead=True       
                        except:                            
                            logger.info("{logStr:s}{dbFileMxPkl:s} read error! - reading SIR 3S raw data ...".format(
                                 logStr=logStr
                                ,dbFileMxPkl=logPathOutputFct(dbFileMxPkl)                                
                                )
                                )                        
                        
                        
        
        if not dbFileMxPklRead:
        
            ### Modellergebnisse lesen
            try:
                mx=Mx.Mx(mx1File,maxRecords=maxRecords)
                logger.debug("{0:s}{1:s}".format(logStr,'MX read ok so far.'))   
            except Mx.MxError:
                logStrFinal="{logStr:s}mx1File: {mx1File:s}: MxError!".format(
                    logStr=logStr
                    ,mx1File=logPathOutputFct(mx1File)) 
                m = dxWithMx(dx,None,crs)
                raise readDxAndMxError(logStrFinal)     
                
            ### Vector-Results 2 MxDf
            if mxsVecsResults2MxDf != None:
                try:                
                    df=mx.readMxsVecsResultsForObjectType(Sir3sVecIDReExp=mxsVecsResults2MxDf,flatIndex=False)                    
                    logger.debug("{logStr:s} df from readMxsVecsResultsForObjectType: {dfStr:s}".format(
                        logStr=logStr,dfStr=df.head(5).to_string()))
                    
                    # Kanalweise bearbeiten
                    vecChannels=sorted(list(set(df.index.get_level_values(1))))
                    
                    V3_VBEL=dx.dataFrames['V3_VBEL']
                    
                    
                    mxVecChannelDfs={}
                    for vecChannel in vecChannels:
                        
                        #print(vecChannel)
                        
                        dfVecChannel=df.loc[(slice(None),vecChannel,slice(None),slice(None)),:]
                        dfVecChannel.index=dfVecChannel.index.get_level_values(2).rename('TIME')
                        dfVecChannel=dfVecChannel.dropna(axis=1,how='all')
                        
                        mObj=re.search(Mx.regExpSir3sVecIDObjAtr,vecChannel)                    
                        OBJTYPE,ATTRTYPE=mObj.groups()
                               
                        # Zeiten aendern wg. spaeterem concat mit mx.df
                        dfVecChannel.index=[pd.Timestamp(t,tz='UTC') for t in dfVecChannel.index]
                        
                        if OBJTYPE == 'KNOT':
                            dfOBJT=dx.dataFrames['V_BVZ_KNOT'][['tk','NAME']]
                            dfOBJT.index=dfOBJT['tk']
                            colRenDctToNamesMxDf={col:"{:s}~{!s:s}~*~{:s}~{:s}".format(OBJTYPE,dfOBJT.loc[col,'NAME'],col,ATTRTYPE) for col in dfVecChannel.columns.to_list()}
                        else:    
                            dfOBJT=V3_VBEL[['pk','NAME_i','NAME_k']].loc[(OBJTYPE,slice(None)),:]
                            dfOBJT.index=dfOBJT.index.get_level_values(1) # die OBJID; xk
                            colRenDctToNamesMxDf={col:"{:s}~{!s:s}~{!s:s}~{:s}~{:s}".format(OBJTYPE,dfOBJT.loc[col,'NAME_i'],dfOBJT.loc[col,'NAME_k'],col,ATTRTYPE) for col in dfVecChannel.columns.to_list()}
                                  
                        dfVecChannel=dfVecChannel.rename(columns=colRenDctToNamesMxDf)
                        
                        mxVecChannelDfs[vecChannel]=dfVecChannel         
                                            
                    l=mx.df.columns.to_list()
                    logger.debug("{:s} Anzahl der Spalten vor Ergaenzung der Vektorspalten: {:d}".format(logStr,len(l)))
                        
                    mx.df=pd.concat([mx.df]
                    +list(mxVecChannelDfs.values())               
                    ,axis=1)
                    
                    l=mx.df.columns.to_list()
                    logger.debug("{:s} Anzahl der Spalten nach Ergaenzung der Vektorspalten: {:d}".format(logStr,len(l)))                
                    
                    # Test auf mehrfach vorkommende Spaltennamen                
                    l=mx.df.loc[:,mx.df.columns.duplicated()].columns.to_list()
                    if len(l)>0:
                        logger.debug("{:s} Anzahl der Spaltennamen die mehrfach vorkommen: {:d}; eliminieren der mehrfach vorkommenden ... ".format(logStr,len(l)))
                        mx.df = mx.df.loc[:,~mx.df.columns.duplicated()]
                           
                    l=mx.df.columns.to_list()    
                    logger.debug("{:s} Anzahl der Spalten nach Ergaenzung der Vektorspalten und nach eliminieren der mehrfach vorkommenden: {:d}".format(logStr,len(l)))
                        
                        
                except Mx.MxError:
                    logStrFinal="{logStr:s}mxsVecsResults2MxDf failed".format(logStr=logStr)     
                    raise readDxAndMxError(logStrFinal)             
        
            ### Vector-Results 2 MxDfVecAggs
            if mxsVecsResults2MxDfVecAggs != None:
                try:         
                    for idxTime in mxsVecsResults2MxDfVecAggs:
                        try:
                            aTime=mx.df.index[idxTime]
                        except:
                            logger.info(f"{logStr}: Requested Timestep {idxTime} not in MX-Results.")  
                            continue
                        
                        df,tL,tR=mx.getVecAggs(time1st=aTime,aTIME=True)
                                            
                except Mx.MxError:
                    logStrFinal="{logStr:s}mxsVecsResults2MxDf failed".format(logStr=logStr)     
                    raise readDxAndMxError(logStrFinal)             

        
            if not preventPklDump:
                if isfile(dbFileMxPkl):
                    logger.info("{logStr:s}{dbFileMxPkl:s} exists and is overwritten...".format(
                         logStr=logStr
                        ,dbFileMxPkl=logPathOutputFct(dbFileMxPkl)                        
                        )
                        )
                else:
                    logger.info("{logStr:s}{dbFileMxPkl:s} is written ...".format(
                         logStr=logStr
                        ,dbFileMxPkl=logPathOutputFct(dbFileMxPkl)                        
                        )
                        )                                                                
                with open(dbFileMxPkl,'wb') as f:  
                    pickle.dump(mx,f)     
            else:
                pass
                                             
        dbFileDxMxPklRead=False
        dbFileDxMxPkl="{:s}-m.pkl".format(dbFilename)        
        
        if preventPklDump:        
            if isfile(dbFileDxMxPkl):
                      logger.info("{logStr:s}{dbFileDxMxPkl:s} exists and is deleted...".format(
                           logStr=logStr
                          ,dbFileDxMxPkl=logPathOutputFct(dbFileDxMxPkl)                        
                          )
                          )
                      os.remove(dbFileDxMxPkl)        
        else:
            logger.debug("{logStrPrefix:s}corresp. dbFileDxMxPkl-File: {dbFileDxMxPkl:s}".format(
                logStrPrefix=logStr
                ,dbFileDxMxPkl=logPathOutputFct(dbFileDxMxPkl)
                ))
                
        if not forceSir3sRead:            
            # Pkl existiert
            if os.path.exists(dbFileDxMxPkl):                
                # ist eine Datei und lesbar
                if isfile(dbFileDxMxPkl) and access(dbFileDxMxPkl,R_OK):
                    # ist neuer als mx1File und dbFile
                    
                    tMx1=os.path.getmtime(mx1File)
                    tDb=os.path.getmtime(dbFile)
                    tPkl=os.path.getmtime(dbFileDxMxPkl)
                                                            
                    if (tMx1 < tPkl) and (tDb < tPkl):
                        logger.info("{logStr:s}{dbFileDxMxPkl:s} newer than {mx1File:s} and {dbFile:s} and therefore read ...".format(
                             logStr=logStr
                            ,dbFileDxMxPkl=logPathOutputFct(dbFileDxMxPkl)
                            ,mx1File=logPathOutputFct(mx1File)
                            ,dbFile=logPathOutputFct(dbFile)
                            )
                            )                        
                        try:
                           with open(dbFileDxMxPkl,'rb') as f:  
                               m=pickle.load(f)  
                           dbFileDxMxPklRead=True    
                        except:                            
                            logger.info("{logStr:s}{dbFileDxMxPkl:s} read error! - processing dx and mx ...".format(
                                 logStr=logStr
                                ,dbFileDxMxPkl=logPathOutputFct(dbFileDxMxPkl)                                
                                )
                                )                            
                                                    
        if not dbFileDxMxPklRead:
            #
            m = dxWithMx(dx,mx,crs)
            
            if not preventPklDump:
                if isfile(dbFileDxMxPkl):
                    logger.info("{logStr:s}{dbFileDxMxPkl:s} exists and is overwritten...".format(
                         logStr=logStr
                        ,dbFileDxMxPkl=logPathOutputFct(dbFileDxMxPkl)                        
                        )
                        )
                else:
                    logger.info("{logStr:s}{dbFileDxMxPkl:s} is written ...".format(
                         logStr=logStr
                        ,dbFileDxMxPkl=logPathOutputFct(dbFileDxMxPkl)                        
                        )
                        )                                                                
                with open(dbFileDxMxPkl,'wb') as f:  
                    pickle.dump(m,f)       
            
            else:
                pass
                # if isfile(dbFileDxMxPkl):
                #           logger.info("{logStr:s}{dbFileDxMxPkl:s} exists and is deleted...".format(
                #                logStr=logStr
                #               ,dbFileDxMxPkl=dbFileDxMxPkl                        
                #               )
                #               )
                #           os.remove(dbFileDxMxPkl)
            
        else:
            pass
        
                               
    except readDxAndMxGoto:        
        logger.info(logStrFinal)    

    except Exception as e:
        logStrFinal="{:s}Exception: Line: {:d}: {!s:s}: {:s}".format(logStr,sys.exc_info()[-1].tb_lineno,type(e),str(e))
        logger.error(logStrFinal)         
    finally:
        logger.debug("{0:s}{1:s}".format(logStr,'_Done.'))  
        return m



class readMxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def readMx(rootdir, logPathOutputFct=os.path.relpath):
    """
    Reads SIR 3S results and returns a Mx object.

    :param rootdir: Path to root directory of the Model. The results are read into a Mx object via the mx files.
    :type rootdir: str
    :param logPathOutputFct: logPathOutputFct(fileName) is used for logoutput of filenames unless explicitly stated otherwise in the logoutput. Defaults to os.path.relpath.
    :type logPathOutputFct: function, optional

    :return: Mx object with two attributes: 
             - mx.df: pandas-Df ('time curve data') from from SIR 3S' MXS file(s)
             - mx.dfVecAggs: pandas-Df ('vector data') from SIR 3S' MXS file(s)
    :rtype: Mx object
    """
    
    mx=None
    
    logStrPrefix = "{0:s}.{1:s}: ".format(__name__, sys._getframe().f_code.co_name)
    logger.debug("{0:s}Start.".format(logStrPrefix))   
    
    try:
        # Use glob to find all MX1 files in the directory
        mx1_files = glob.glob(os.path.join(rootdir, '**', '*.MX1'), recursive=True)

        # Get the parent directories of the MX1 files
        parent_dirs = set(os.path.dirname(file) for file in mx1_files)

        # Check the number of directories found
        if len(parent_dirs) > 1:
            logger.error("{0:s}Mehr als ein Verzeichnis mit MX1-Dateien gefunden.".format(logStrPrefix))
            for dir in parent_dirs:
                logger.error("{0:s}Verzeichnis: {1:s}".format(logStrPrefix, dir))
            raise readMxError("Mehr als ein Verzeichnis mit MX1-Dateien gefunden.")
        elif len(parent_dirs) == 1:
            wDirMx = list(parent_dirs)[0]
        else:
            logger.error("{0:s}Keine Verzeichnisse mit MX1-Dateien gefunden.".format(logStrPrefix))
            raise readMxError("Keine Verzeichnisse mit MX1-Dateien gefunden.")
    except Exception as e:
        logger.error("{0:s}Ein Fehler ist aufgetreten beim Suchen von MX1-Verzeichnissen: {1:s}".format(logStrPrefix, str(e)))
        raise
    
    try:
        logger.debug("{0:s}wDirMx von abspath von wDir von dbFile: {1:s}".format(logStrPrefix, wDirMx))
        
        wDirMxMx1Content=glob.glob(os.path.join(wDirMx,'*.MX1'))
        wDirMxMx1Content=sorted(wDirMxMx1Content) 

        if len(wDirMxMx1Content)>1:
            logger.debug("{0:s}Mehr als 1 ({1:d}) MX1 in wDirMx vorhanden.".format(logStrPrefix, len(wDirMxMx1Content)))
        mx1File= wDirMxMx1Content[0]
        logger.debug("{0:s}mx1File: {1:s}".format(logStrPrefix, logPathOutputFct(mx1File)))
        
    except:
        logger.info("{0:s}Problem mit dem MX1-Dateipfad".format(logStrPrefix))
        
    try:
        mx=Mx.Mx(mx1File)
        logger.debug("{0:s}MX wurde bisher erfolgreich gelesen. {1:s}".format(logStrPrefix, mx1File))   
    except Mx.MxError:  
        logger.info("{0:s}MX1-Datei konnte nicht gelesen werden".format(logStrPrefix))
    finally:
        logger.debug("{0:s}_Done.".format(logStrPrefix)) 
    
    return mx
