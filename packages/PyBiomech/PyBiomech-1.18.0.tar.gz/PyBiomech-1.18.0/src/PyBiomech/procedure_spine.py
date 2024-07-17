"""
.. module:: procedure_or
   :synopsis: helper module for procedures used with Oxford-Rig (IORT UZLeuven)

"""

import numpy as np

from . import fio, kine, spine

import os
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
from .pyver import __pyver
if __pyver == 3:
    matplotlib.use('Qt5Agg')
else:
    matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from . import utils
from . import geom
    
    
    

def performSpineAnalysis1(
                        markers,
                        spinePointNames,
                        resultsDir,
                        anglesDef = {},
                        frames = None,
                        sagSpineSplineOrder=3,
                        froSpineSplineOrder=3,
                        useCustomSpineModelDef=False,
                        customSpineModelDef=None,
                        savePlots=True,
                        ):

    # Calculate PELVIS anatomical reference frame for acquisition system
    allPelvisVisible = set(['RASI','LASI','RPSI','LPSI']) <= set(markers.keys())
    if allPelvisVisible:
        RPel, OPel = kine.pelvisPoseISB(markers, s='R')
    else:
        RPel, OPel = kine.pelvisPoseNoOneASI(markers, s='R')
    RTPel = kine.composeRotoTranslMatrix(RPel, OPel)
    RTPeli = kine.inv2(RTPel)
    
    markersNew = markers.copy()
    
    # Express spine points in pelvis reference frame
    spinePointNamesNew = spinePointNames[:]
    AIAPointNames = ['Apex top', 'Inflex', 'Apex bottom']
    spinePointNamesNewAll = spinePointNamesNew + AIAPointNames
    for i, m in enumerate(spinePointNames):
        # If wanted point name does not exist
        if m not in markersNew:
            # If wanted point is a True-type point
            if m.find('True') > -1:
                spinePointNamesNew[i] = m[5:]
    spinePoints = {m: markersNew[m] for m in spinePointNamesNew}
    spinePointsPel = kine.changeMarkersReferenceFrame(spinePoints, RTPeli)
    
    # Create extra points of interest
    extraPoints = {}
    extraPoints['C7 for CVA'] = markersNew['True C7'].copy()
    extraPoints['C7 for CVA'][:,2] = markersNew['True SACR'][:,2]
    extraPoints['STRN'] = markersNew['STRN'].copy()
    extraPoints['CLAV'] = markersNew['CLAV'].copy()
    extraPoints['RSHO'] = markersNew['RSHO'].copy()
    extraPoints['LSHO'] = markersNew['LSHO'].copy()
    extraPoints['RASI'] = markersNew['RASI'].copy()
    extraPoints['LASI'] = markersNew['LASI'].copy()
    extraPoints['RPSI'] = markersNew['RPSI'].copy()
    extraPoints['LPSI'] = markersNew['LPSI'].copy()
    extraPointsPel = kine.changeMarkersReferenceFrame(extraPoints, RTPeli)
    
    # Merge spine points in one array
    spineData = np.stack([spinePointsPel[m] for m in spinePointNamesNew], axis=2)  # Nf x 3 x Np
    extraPointNames = [
        'C7 for CVA', 
        'STRN', 
        'CLAV',
        'RSHO', 
        'LSHO',
        'RASI',
        'LASI',
        'RPSI',
        'LPSI'
    ]
    extraData = np.stack([extraPointsPel[m] for m in extraPointNames], axis=2)  # Nf x 3 x Ne
    
    # Init results
    res = {}
    res['newMarkers'] = markersNew
    res['newMarkers'].update(extraPoints)
    sup, inf = spinePointNamesNew[:-1], spinePointNamesNew[1:]
    spineAngleNames = [sup[i] + '_' + inf[i] for i in range(len(sup))]
    Nf = spineData.shape[0]
    res['spineAngles'] = {}
    res['spineAngles']['sagittal'] = {a: np.zeros((Nf,)) for a in spineAngleNames}
    res['spineAngles']['frontal'] = {a: np.zeros((Nf,)) for a in spineAngleNames}
    customAngleNames = anglesDef.keys()
    for angleName in customAngleNames:
        space = anglesDef[angleName][0]
        res['spineAngles'][space][angleName] = np.zeros((Nf,))
    res['extraData'] = {}
    res['extraData']['SVA'] = np.zeros((Nf,))
    res['extraData']['SagApexTopHeight'] = np.zeros((Nf,))
    res['extraData']['SagInflexHeight'] = np.zeros((Nf,))
    res['extraData']['SagApexBottomHeight'] = np.zeros((Nf,))
    
    # Create results directory if not existing
    if not os.path.exists(resultsDir):
        os.mkdir(resultsDir)
        
    iRange = range(Nf)
    if frames is not None:
        iRange = frames
    
    # Process data
    for i in iRange:
        
        print('processing time frame %d ...' % i)        
        
        # Interpolate spline in sagittal plane
        #spineDataSag = spineData[i,0:2,:].T # Np x 2
        spineDataSag = spineData[i,1::-1,:].T # Np x 2
        spineDataSagSort = np.argsort(spineDataSag[:,0])[::-1]
        spineDataSagSort = range(spineDataSag.shape[0])
        spineDataSag = spineDataSag[spineDataSagSort,:]
        extraDataSag = extraData[i,1::-1,:].T # Ne x 2
        normalSlopesSagCustom = np.nan * np.ones((spineDataSag.shape[0],))
        
        if not useCustomSpineModelDef:
            
            print('using ordinary spine model ')
            
            spineLineSag = spine.create2DPolynomial(spineDataSag, order=sagSpineSplineOrder)[:,:,np.newaxis]
            
            # Calculate slope of spine normal at the wanted points
            spineLineSagDer = spine.calcPolynomialTangentSlopes(spineDataSag, u='only_pts', k=sagSpineSplineOrder)[:,:,np.newaxis]
        
        else:
            
            print('using custom spine model ')

            Nc = len(customSpineModelDef['model_sag'])

            spinePointNamesNewSag = [spinePointNamesNew[p] for p in spineDataSagSort]

            # spineLineSag = np.zeros((1,2))
            spineLineSag = np.nan * np.zeros((200, 2, Nc))
            # spineLineSagDer = np.nan * np.ones(spineDataSag.shape)
            spineLineSagDer = np.nan * np.ones((spineDataSag.shape[0], spineDataSag.shape[1], Nc))
            
            for c, defPW in enumerate(customSpineModelDef['model_sag']):
                
                print('using segment "%s"' % defPW['name'])
                
                pointStartPW = defPW['point_start']
                pointStopPW = defPW['point_stop']
                sPW = spinePointNamesNewSag.index(pointStartPW)
                ePW = spinePointNamesNewSag.index(pointStopPW) + 1
                nPW = ePW - sPW
                pointRefStartPW = defPW['point_ref_start']
                pointRefStopPW = defPW['point_ref_stop']
                srPW = spinePointNamesNewSag.index(pointRefStartPW)
                erPW = spinePointNamesNewSag.index(pointRefStopPW) + 1
                nrPW = erPW - srPW
                orderPW = defPW['order']
                xyPW = defPW['xy']
                weightsPW = np.ones((nrPW,))
                if 'weights' in defPW:
                    for weightPW in defPW['weights']:
                        iPW = spinePointNamesNewSag.index(weightPW['point']) - srPW
                        weightsPW[iPW] = weightPW['value']
                
                spineDataSagPW = spineDataSag[srPW:erPW,:]
                
                spineLineSagPW = spine.create2DPolynomial(spineDataSagPW, order=orderPW, weights=weightsPW, xy=xyPW)
                # spineLineSag = np.vstack((spineLineSag[:-1,:], spineLineSagPW))
                spineLineSag[:spineLineSagPW.shape[0],:,c] = spineLineSagPW

                spineLineSagDerPW = spine.calcPolynomialTangentSlopes(spineDataSagPW, u='only_pts', k=orderPW, weights=weightsPW, xy=xyPW)
                # spineLineSagDer[sPW:ePW,:] = spineLineSagDerPW
                spineLineSagDer[sPW:ePW,:,c] = spineLineSagDerPW[sPW-srPW:sPW-srPW+nPW,:]  


            for c, defPW in enumerate(customSpineModelDef['normal_custom_sag']):

                print('using custom normal "%s"' % defPW['name'])

                pointPW = defPW['point']
                methodPW = defPW['method']
                dataPW = defPW['data']
                sPW = spinePointNamesNewSag.index(pointPW)
                ePW = sPW + 1

                if methodPW == 'line_through_points':

                    pointNames = dataPW
                    idx1 = [extraPointNames.index(p) for p in pointNames if p in extraPointNames]
                    idx2 = [spinePointNamesNew.index(p) for p in pointNames if p in spinePointNamesNew]
                    points = np.vstack((extraDataSag[idx1,:], spineDataSag[idx2,:]))
                    _, vec = geom.fitLineThroughPointsWithPCA(points)

                else:

                    raise Exception("method %s not implemented" % methodPW)

                normalSlopesSagCustom[sPW:ePW] = np.tan(np.arctan2(vec[0], vec[1]))


        Np = spineDataSag.shape[0]
        
        # normalSlopesSag = -spineLineSagDer[:,1] / spineLineSagDer[:,0]
        # normalSlopesSag = np.nanmean(-spineLineSagDer[:,1,:] / spineLineSagDer[:,0,:], axis=1)
        normalSlopesSag = np.tan( np.nanmean(np.arctan2(-spineLineSagDer[:,1,:], spineLineSagDer[:,0,:]), axis=1) )
        normalInterceptsSag = spineDataSag[:,0] - normalSlopesSag * spineDataSag[:,1]

        normalInterceptsSagCustom = spineDataSag[:,0] - normalSlopesSagCustom * spineDataSag[:,1]
        
        # Search apex and inflexion points (AIA)
        AIASagOK = True
        uDense = np.arange(0, 1.001, 0.001)
        der1Dense = spine.calcPolynomialDerivatives(spineDataSag, u=uDense, k=sagSpineSplineOrder, der=1)[:,1]
        ndxDer1ChangeSign = np.append(np.diff(np.sign(der1Dense)), [False]) != 0
#        spineDataAIASag = spine.evalPolynomial(spineDataSag, u=uDense[ndxDer1ChangeSign], k=sagSpineSplineOrder)
#        plt.plot(spineLineSag[:,1], spineLineSag[:,0], lw=3)
#        plt.plot(spineDataAIASag[:,1], spineDataAIASag[:,0], 'rx')
#        plt.show()
        if ndxDer1ChangeSign.sum() != 2:
#            raise Exception('sagittal: there seems to be not exactly 2 apex points')
            AIASagOK = False
        if AIASagOK:
            der2Dense = spine.calcPolynomialDerivatives(spineDataSag, u=uDense, k=sagSpineSplineOrder, der=2)[:,1]
            ndxDer2ChangeSign = np.append(np.diff(np.sign(der2Dense)), [False]) != 0
            win = np.cumsum(ndxDer1ChangeSign)
            win[win != 1] = 0
            win = win.astype(bool)
            ndxDer2ChangeSign = ndxDer2ChangeSign & win
            if ndxDer2ChangeSign.sum() != 1:
#                raise Exception('sagittal: there seems to be not exactly 1 inflection point')
                AIASagOK = False
        if AIASagOK:
            ndxU = ndxDer1ChangeSign | ndxDer2ChangeSign
            spineDataAIASag = spine.evalPolynomial(spineDataSag, u=uDense[ndxU], k=sagSpineSplineOrder)
        else:
            spineDataAIASag = np.nan * np.zeros((3, 2))
        res['extraData']['SagApexTopHeight'][i] = spineDataAIASag[0,0]
        res['extraData']['SagInflexHeight'][i] = spineDataAIASag[1,0]
        res['extraData']['SagApexBottomHeight'][i] = spineDataAIASag[2,0]
        spineDataSagAll = np.vstack((spineDataSag, spineDataAIASag))
        
        # Calculate slope of spine normal at the wanted points (AIA)
        spineLineAIASagDer = spine.calcPolynomialTangentSlopes(spineDataAIASag, u='only_pts', k=sagSpineSplineOrder)
        normalSlopesAIASag = -spineLineAIASagDer[:,1] / spineLineAIASagDer[:,0]
        normalInterceptsAIASag = spineDataAIASag[:,0] - normalSlopesAIASag * spineDataAIASag[:,1]
        
        normalSlopesSagAll = np.concatenate((normalSlopesSag, normalSlopesAIASag))
        normalInterceptsSagAll = np.concatenate((normalInterceptsSag, normalInterceptsAIASag))

        # Calculate angles between segments
        m1, m2 = normalSlopesSag[:-1], normalSlopesSag[1:]
        q1, q2 = normalInterceptsSag[:-1], normalInterceptsSag[1:]
        xCrossPoint = (q2 - q1) / (m1 - m2)
#        yCrossPoint = m1 * xCrossPoint + q1
        angleSign = (xCrossPoint > spineDataSag[:-1,1]) & (xCrossPoint > spineDataSag[1:,1])
        angleSign = 2 * (angleSign - 0.5)
        angles = angleSign * spine.calcInterlinesAngle(m1, m2)
        for j in range(len(spineAngleNames)):
            res['spineAngles']['sagittal'][spineAngleNames[j]][i] = angles[j]
            
        # Calculate SVA
        SVASign = extraDataSag[0,1] > spineDataSag[-1,1]
        SVASign = 2 * (SVASign - 0.5)
        res['extraData']['SVA'][i] = SVASign * np.linalg.norm(spineDataSag[-1,:] - extraDataSag[0,:])
            
        # Interpolate spline in frontal plane
#        spineDataFro = spineData[i,2:0:-1,:].T # Np x 2
        spineDataFro = spineData[i,1:,:].T # Np x 2
        spineDataFroSort = np.argsort(spineDataFro[:,0])[::-1]
        spineDataFroSort = range(spineDataFro.shape[0])
        spineDataFro = spineDataFro[spineDataFroSort,:]
        extraDataFro = extraData[i,1:,:].T # Ne x 2
        normalSlopesFroCustom = np.nan * np.ones((spineDataFro.shape[0],))
        
        if not useCustomSpineModelDef:
            
            print('using ordinary spine model ')
        
            spineLineFro = spine.create2DPolynomial(spineDataFro, order=froSpineSplineOrder)[:,:,np.newaxis]
            
            # Calculate slope of spine normal at the wanted points
            spineLineFroDer = spine.calcPolynomialTangentSlopes(spineDataFro, u='only_pts', k=froSpineSplineOrder)[:,:,np.newaxis]
            
        else:
            
            print('using custom spine model ')

            Nc = len(customSpineModelDef['model_fro'])

            spinePointNamesNewFro = [spinePointNamesNew[p] for p in spineDataFroSort]

            # spineLineFro = np.zeros((1,2))
            spineLineFro = np.nan * np.zeros((200, 2, Nc))
            # spineLineFroDer = np.nan * np.ones(spineDataFro.shape)
            spineLineFroDer = np.nan * np.ones((spineDataFro.shape[0], spineDataFro.shape[1], Nc))
            
            for c, defPW in enumerate(customSpineModelDef['model_fro']):
                
                print('using segment "%s"' % defPW['name'])
                
                pointStartPW = defPW['point_start']
                pointStopPW = defPW['point_stop']
                sPW = spinePointNamesNewFro.index(pointStartPW)
                ePW = spinePointNamesNewFro.index(pointStopPW) + 1
                nPW = ePW - sPW
                pointRefStartPW = defPW['point_ref_start']
                pointRefStopPW = defPW['point_ref_stop']
                srPW = spinePointNamesNewFro.index(pointRefStartPW)
                erPW = spinePointNamesNewFro.index(pointRefStopPW) + 1
                nrPW = erPW - srPW
                orderPW = defPW['order']
                xyPW = defPW['xy']
                weightsPW = np.ones((nrPW,))
                if 'weights' in defPW:
                    for weightPW in defPW['weights']:
                        iPW = spinePointNamesNewFro.index(weightPW['point']) - srPW
                        weightsPW[iPW] = weightPW['value']
                
                spineDataFroPW = spineDataFro[srPW:erPW,:]
                
                spineLineFroPW = spine.create2DPolynomial(spineDataFroPW, order=orderPW, weights=weightsPW, xy=xyPW)
                # spineLineFro = np.vstack((spineLineFro[:-1,:], spineLineFroPW))
                spineLineFro[:spineLineFroPW.shape[0],:,c] = spineLineFroPW

                spineLineFroDerPW = spine.calcPolynomialTangentSlopes(spineDataFroPW, u='only_pts', k=orderPW, weights=weightsPW, xy=xyPW)
                # spineLineFroDer[sPW:ePW,:] = spineLineFroDerPW
                spineLineFroDer[sPW:ePW,:,c] = spineLineFroDerPW[sPW-srPW:sPW-srPW+nPW,:]


            for c, defPW in enumerate(customSpineModelDef['normal_custom_fro']):

                print('using custom normal "%s"' % defPW['name'])

                pointPW = defPW['point']
                methodPW = defPW['method']
                dataPW = defPW['data']
                sPW = spinePointNamesNewSag.index(pointPW)
                ePW = sPW + 1

                if methodPW == 'line_through_points':

                    pointNames = dataPW
                    idx1 = [extraPointNames.index(p) for p in pointNames if p in extraPointNames]
                    idx2 = [spinePointNamesNew.index(p) for p in pointNames if p in spinePointNamesNew]
                    points = np.vstack((extraDataFro[idx1,:], spineDataFro[idx2,:]))
                    _, vec = geom.fitLineThroughPointsWithPCA(points)

                else:

                    raise Exception("method %s not implemented" % methodPW)

                normalSlopesFroCustom[sPW:ePW] = np.tan(np.arctan2(vec[0], vec[1]))
            
        Np = spineDataFro.shape[0]

        # normalSlopesFro = -spineLineFroDer[:,1] / spineLineFroDer[:,0]
        # normalSlopesFro = np.nanmean(-spineLineFroDer[:,1,:] / spineLineFroDer[:,0,:], axis=1)
        normalSlopesFro = np.tan( np.nanmean(np.arctan2(-spineLineFroDer[:,1,:], spineLineFroDer[:,0,:]), axis=1) )
        normalInterceptsFro = spineDataFro[:,0] - normalSlopesFro * spineDataFro[:,1]

        normalInterceptsFroCustom = spineDataFro[:,0] - normalSlopesFroCustom * spineDataFro[:,1]

        # Calculate angles between segments
        m1, m2 = normalSlopesFro[:-1], normalSlopesFro[1:]
        q1, q2 = normalInterceptsFro[:-1], normalInterceptsFro[1:]
        xCrossPoint = (q2 - q1) / (m1 - m2)
#        yCrossPoint = m1 * xCrossPoint + q1
        angleSign = (xCrossPoint > spineDataFro[:-1,1]) & (xCrossPoint > spineDataFro[1:,1])
        angleSign = 2 * (angleSign - 0.5)
        angles = angleSign * spine.calcInterlinesAngle(m1, m2)
        for j in range(len(spineAngleNames)):
            res['spineAngles']['frontal'][spineAngleNames[j]][i] = angles[j]
            
        # Calculate custom angles
        for angleName in customAngleNames:
            plane = anglesDef[angleName][0]
            p1 = anglesDef[angleName][1]
            source1 = anglesDef[angleName][2]
            p2 = anglesDef[angleName][3]
            source2 = anglesDef[angleName][4]
            if not useCustomSpineModelDef and (source1 == 'from_custom_normals' or source2 == 'from_custom_normals'):
                raise Exception('if custom spine model is not used, custom angle normal sources can only be "from_spine_profile"')
            # normal 1
            if plane == 'sagittal':
                if source1 == 'from_spine_profile':
                    normalSlopes = normalSlopesSagAll
                    normalIntercepts = normalInterceptsSagAll
                elif source1 == 'from_custom_normals':
                    normalSlopes = normalSlopesSagCustom
                    normalIntercepts = normalInterceptsSagCustom
                else:
                    raise Exception('normal source1 %s not implemented' % source1)                  
            elif plane == 'frontal':
                if source1 == 'from_spine_profile':
                    normalSlopes = normalSlopesFro
                    normalIntercepts = normalInterceptsFro
                elif source1 == 'from_custom_normals':
                    normalSlopes = normalSlopesFroCustom
                    normalIntercepts = normalInterceptsFroCustom 
                else:
                    raise Exception('normal source1 %s not implemented' % source1)    
            try:
                i1 = spinePointNamesNewAll.index(p1)
            except:
                raise Exception('%s name is not recognized' % p1)
            m1 = normalSlopes[i1]
            q1 = normalIntercepts[i1]
            # normal 2
            if plane == 'sagittal':
                if source2 == 'from_spine_profile':
                    normalSlopes = normalSlopesSagAll
                    normalIntercepts = normalInterceptsSagAll
                elif source2 == 'from_custom_normals':
                    normalSlopes = normalSlopesSagCustom
                    normalIntercepts = normalInterceptsSagCustom  
                else:
                    raise Exception('normal source2 %s not implemented' % source2)                  
            elif plane == 'frontal':
                if source2 == 'from_spine_profile':
                    normalSlopes = normalSlopesFro
                    normalIntercepts = normalInterceptsFro
                elif source2 == 'from_custom_normals':
                    normalSlopes = normalSlopesFroCustom
                    normalIntercepts = normalInterceptsFroCustom  
                else:
                    raise Exception('normal source2 %s not implemented' % source2) 
            try:
                i2 = spinePointNamesNewAll.index(p2)
            except:
               raise Exception('%s name is not recognized' % p2)
            m2 = normalSlopes[i2]
            q2 = normalIntercepts[i2]
            # angle
            xCrossPoint = (q2 - q1) / (m1 - m2)
#            yCrossPoint = m1 * xCrossPoint + q1
            if plane == 'sagittal':
                angleSign = (xCrossPoint > spineDataSagAll[i1,1]) & (xCrossPoint > spineDataSagAll[i2,1])
            elif plane == 'frontal':
                angleSign = (xCrossPoint > spineDataFro[i1,1]) & (xCrossPoint > spineDataFro[i2,1])
            angleSign = 2 * (angleSign - 0.5)
            angle = angleSign * spine.calcInterlinesAngle(m1, m2)
            res['spineAngles'][plane][angleName][i] = angle
        
        if savePlots:
            
            # Create results directory if not existing
            figuresDir = os.path.join(resultsDir, 'figures')
            if not os.path.exists(figuresDir):
                os.mkdir(figuresDir)
            
            # Plot spine in 3D
#            fig = plt.figure()
#            ax = fig.gca(projection='3d')
#            ax.scatter(spineData[i,2,:], spineData[i,0,:], spineData[i,1,:])
#            mplh.set_axes_equal(ax)
#            plt.show()
            
            # Plot spine in sagittal/frontal plane
            plt.clf()
            
            plt.subplot(1, 2, 1)
            plt.plot(spineDataSag[:,1], spineDataSag[:,0], 'o')
            # plt.plot(spineLineSag[:,1], spineLineSag[:,0], lw=3)
            plt.plot(spineLineSag[:,1,:], spineLineSag[:,0,:], lw=3)
            plt.plot(spineDataAIASag[:,1], spineDataAIASag[:,0], 'rx')
            plt.plot(extraDataSag[:1,1], extraDataSag[:1,0], 'bo')
            plt.plot(extraDataSag[1:,1], extraDataSag[1:,0], 'yo')
            ax = plt.gca()
            xlim, ylim = ax.get_xlim(), ax.get_ylim()
            xN = np.tile([-1000, 1000], [Np, 1])
            yN = (xN - spineDataSag[:,1][:,None]) * normalSlopesSag[:,None] + spineDataSag[:,0][:,None]
            plt.plot(xN.T, yN.T, 'k')
            yN = (xN - spineDataSag[:,1][:,None]) * normalSlopesSagCustom[:,None] + spineDataSag[:,0][:,None]
            plt.plot(xN.T, yN.T, color='grey')
#            plt.plot(xCrossPoint, yCrossPoint, 'bo')
            plt.axis('equal')
            ax.set_xlim(xlim)
#            ax.set_xlim((-500,100))
            ax.set_ylim(ylim)
            plt.title('Sagittal')
            plt.xlabel('X pelvis (anterior +)')
            plt.ylabel('Y pelvis (up +)')
            
            plt.subplot(1, 2, 2)
#            plt.plot(spineData[i,2,:], spineData[i,1,:], 'o')
#            plt.axis('equal')
#            plt.title('Frontal')
#            plt.xlabel('Z pelvis (right +)')
            plt.plot(spineDataFro[:,1], spineDataFro[:,0], 'o')
            # plt.plot(spineLineFro[:,1], spineLineFro[:,0], lw=3)
            plt.plot(spineLineFro[:,1,:], spineLineFro[:,0,:], lw=3)
            plt.plot(extraDataFro[:1,1], extraDataFro[:1,0], 'bo')
            plt.plot(extraDataFro[1:,1], extraDataFro[1:,0], 'yo')
            ax = plt.gca()
            xlim, ylim = ax.get_xlim(), ax.get_ylim()
            xN = np.tile([-1000, 1000], [Np, 1])
            yN = (xN - spineDataFro[:,1][:,None]) * normalSlopesFro[:,None] + spineDataFro[:,0][:,None]
            plt.plot(xN.T, yN.T, 'k')
            yN = (xN - spineDataFro[:,1][:,None]) * normalSlopesFroCustom[:,None] + spineDataFro[:,0][:,None]
            plt.plot(xN.T, yN.T, color='grey')
            plt.axis('equal')
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            plt.title('Frontal')
            plt.xlabel('Z pelvis (right +)')
            
            plt.savefig(os.path.join(figuresDir, 'tf_%04d.png' % i), format='png', orientation='landscape')
    
    plt.close('all')
    
    # Create MATLAB-friendly reslts structure
    resML = res.copy()
    resML['newMarkers'] = utils.adjustDictForML(res['newMarkers'])        
    resML['spineAngles']['sagittal'] = utils.adjustDictForML(res['spineAngles']['sagittal'])
    resML['spineAngles']['frontal'] = utils.adjustDictForML(res['spineAngles']['frontal'])
    
    # Save data to MAT file
    fio.writeMATFile(os.path.join(resultsDir, 'results.mat'), resML)
        
    return res
    
    
    


def performSpineAnalysis2(
                        markers,
                        resultsDir,
                        frames = None,
                        savePlots=True,
                        ):
    
    markers2 = markers.copy()
    
    # Calculate PELVIS anatomical reference frame for acquisition system
    allPelvisVisible = set(['RASI','LASI','RPSI','LPSI']) <= set(markers.keys())
    if allPelvisVisible:
        RPel, OPel = kine.pelvisPoseISB(markers, s='R')
    else:
        raise Exception('any of RASI, LASI RPSI LPSI not existing')
    RTPel = kine.composeRotoTranslMatrix(RPel, OPel)
    RTPeli = kine.inv2(RTPel)
    
    # Calculate virtual sacrum point
    markersNew = {}
    markersNew['SACR'] = 0.5 * (markers['RPSI'] + markers['LPSI'])
    if 'L4' not in markers2:
        markersNew['L4'] = 0.5 * (markers['L4R'] + markers['L4L'])
    markers2.update(markersNew)
    
    # Express points in PELVIS anatomical reference frame
    pointNames = [
        'C7',
        'T12',
        'L2',
        'L4L',
        'L4R',
        'L4',
        'LASI',
        'RASI',
        'RPSI',
        'LPSI',
        'SACR'
    ]
    points = {m: markers2[m] for m in pointNames}
    pointsInPel = kine.changeMarkersReferenceFrame(points, RTPeli)
    idxs = {}
    for i in range(len(pointNames)):
        pointName = pointNames[i]
        idxName = 'idx_' + pointName
        idxs[idxName] = i

    colors = [
        'g',
        'b',
        'b',
        'b',
        'b',
        'b',
        'r',
        'r',
        'r',
        'r',
        'r'
    ]
    
    # Merge points in one array
    pointsData = np.stack([pointsInPel[m] for m in pointNames], axis=2)  # Nf x 3 x Np
    
    # Init results
    res = {}
    res['spineAngles'] = {}
    
    # Create results directory if not existing
    if not os.path.exists(resultsDir):
        os.mkdir(resultsDir)
    
    Nf = pointsData.shape[0]
    iRange = range(Nf)
    if frames is not None:
        iRange = frames
        
    if savePlots:
        # Create results directory if not existing
        figuresDir = os.path.join(resultsDir, 'figures')
        if not os.path.exists(figuresDir):
            os.mkdir(figuresDir)
            
    angleT12ToL4ToUpAxisSag = np.zeros((Nf,))
    angleT12ToL4ToUpAxisFro = np.zeros((Nf,))
    angleT12ToSACRToUpAxisSag = np.zeros((Nf,))
    angleT12ToSACRToUpAxisFro = np.zeros((Nf,))
    angleC7ToT12ToUpAxisSag = np.zeros((Nf,))
    angleC7ToT12ToUpAxisFro = np.zeros((Nf,))

    # Process data
    for i in iRange:
        
        print('processing time frame %d ...' % i)        
        
        # caculate data
        pointsDataSag = pointsData[i,1::-1,:].T     # Np x 2
        pointsDataFro = pointsData[i,1:,:].T        # Np x 2
        
        vec = pointsDataSag[idxs['idx_T12'],:] - pointsDataSag[idxs['idx_L4'],:]
        vec = vec[::-1]
        angleT12ToL4ToUpAxisSag[i] = -np.rad2deg(np.arctan2(vec[1], vec[0])) + 90
        
        vec = pointsDataFro[idxs['idx_T12'],:] - pointsDataFro[idxs['idx_L4'],:]
        vec = vec[::-1]
        angleT12ToL4ToUpAxisFro[i] = -np.rad2deg(np.arctan2(vec[1], vec[0])) + 90
        
        vec = pointsDataSag[idxs['idx_T12'],:] - pointsDataSag[idxs['idx_SACR'],:]
        vec = vec[::-1]
        angleT12ToSACRToUpAxisSag[i] = -np.rad2deg(np.arctan2(vec[1], vec[0])) + 90
        
        vec = pointsDataFro[idxs['idx_T12'],:] - pointsDataFro[idxs['idx_SACR'],:]
        vec = vec[::-1]
        angleT12ToSACRToUpAxisFro[i] = -np.rad2deg(np.arctan2(vec[1], vec[0])) + 90
        
        vec = pointsDataSag[idxs['idx_C7'],:] - pointsDataSag[idxs['idx_T12'],:]
        vec = vec[::-1]
        angleC7ToT12ToUpAxisSag[i] = -np.rad2deg(np.arctan2(vec[1], vec[0])) + 90
        
        vec = pointsDataFro[idxs['idx_C7'],:] - pointsDataFro[idxs['idx_T12'],:]
        vec = vec[::-1]
        angleC7ToT12ToUpAxisFro[i] = -np.rad2deg(np.arctan2(vec[1], vec[0])) + 90
        
        if savePlots:
        
            plt.clf()
                
            plt.subplot(1, 2, 1)
            for p in range(len(pointNames)):
                plt.plot(pointsDataSag[p,1], pointsDataSag[p,0], 'o', c=colors[p])
                plt.text(pointsDataSag[p,1]+5, pointsDataSag[p,0], pointNames[p])
            plt.axis('equal')
            plt.title('Sagittal')
            plt.xlabel('X pelvis (anterior +)')
            plt.ylabel('Y pelvis (up +)')
            
            plt.subplot(1, 2, 2)
            for p in range(len(pointNames)):
                plt.plot(pointsDataFro[p,1], pointsDataFro[p,0], 'o', c=colors[p])
                plt.text(pointsDataFro[p,1], pointsDataFro[p,0], pointNames[p])
            plt.axis('equal')
            plt.title('Frontal')
            plt.xlabel('Z pelvis (right +)')
            
            plt.savefig(os.path.join(figuresDir, 'tf_%04d.png' % i), format='png', orientation='landscape')
        
    if savePlots:
        plt.close('all')
        
    res['newMarkers'] = markersNew
    res['spineAngles']['T12ToL4ToUpAxisSag'] = angleT12ToL4ToUpAxisSag
    res['spineAngles']['T12ToL4ToUpAxisFro'] = angleT12ToL4ToUpAxisFro
    res['spineAngles']['T12ToSACRToUpAxisSag'] = angleT12ToSACRToUpAxisSag
    res['spineAngles']['T12ToSACRToUpAxisFro'] = angleT12ToSACRToUpAxisFro
    res['spineAngles']['C7ToT12ToUpAxisSag'] = angleC7ToT12ToUpAxisSag
    res['spineAngles']['C7ToT12ToUpAxisFro'] = angleC7ToT12ToUpAxisFro
    
    return res