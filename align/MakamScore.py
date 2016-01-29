# -*- coding: utf-8 -*-
'''
contains a class
Created on Mar 3, 2014

@author: joro



'''


import os
import sys
import imp
from Phonetizer import Phonetizer
from Decoder import logger
from SymbTrParser2 import SymbTrParser2

# trick to make terminal NOT assume ascii
reload(sys).setdefaultencoding("utf-8")


from utilsLyrics.Utilz import writeListToTextFile, findFileByExtensions
import codecs

import glob
from SymbTrParser import SymbTrParser
# from utils.Utils import writeListToTextFile

import compmusic
from compmusic import dunya
dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')


# 
# COMPOSITION_NAME = 'muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik'
# COMPOSITION_NAME = 'huseyni--sarki--turkaksagi--hicran_oku--sevki_bey'
# 
# PATH_TEST_DATASET='/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/'
# PATH_TEST_DATASET = '/Volumes/IZOTOPE/sertan_sarki/'

class MakamScore():
    '''
    classdocs
    '''


##################################################################################

    def __init__(self, pathToSymbTrFile, pathToSectionTsvFile):
        '''
        Constructor
        
        '''
        self.compositionName = os.path.splitext(pathToSymbTrFile)[0]
        
        ''' lyrics divided into sectons.
        # e.g. "nakarat" : [ word1 word2 ] '''
        
        self._loadSectionsAndSyllablesFromSymbTr(pathToSymbTrFile, pathToSectionTsvFile)
        
        self._lyricsSections2GroupsSimilarMElody()
        
        # pats to individual ..txt lyrics files. 
        self.pathsTolyricSectionFiles = []
        
      
  ##################################################################################

    def _loadSectionsAndSyllablesFromSymbTr(self, pathToSymbTrFile, sectionMetadataFileURI):
        '''
        parses symbTr file. Reads lyrics, 
        reads section names
        groups together section names and lyrics 
        '''
        self.symbTrParser = SymbTrParser2(pathToSymbTrFile, sectionMetadataFileURI)
       
        # list of Word object
        self.symbTrParser.syllables2Lyrics()
        
       
        
     
            
            
    def getLyricsForSection(self, melodicStructure):
        '''
        convenience getter. 
        takes first appearance of melodicStructure
        '''
        

        for section in self.symbTrParser.sections:
            if section.melodicStructure == melodicStructure:
                lyrics = section.lyrics
                break
        if not lyrics.listWords:
            logger.warn("no lyrics for demanded section {} ".format(melodicStructure ))
            return None
        return lyrics 
    
    
    def _lyricsSections2GroupsSimilarMElody(self):
        '''
        divide into groups with similar melody
        '''
        
        self.groupsSimilarMelody = {}
        
        for idx, section in enumerate(self.symbTrParser.sections):
            if section.name != 'VOCAL_SECTION':
                continue
    
            # first letter used as key in dict
            currMelodicStructLetter = section.melodicStructure[0]
            if currMelodicStructLetter not in self.groupsSimilarMelody: # start a new group
                self.groupsSimilarMelody[currMelodicStructLetter] = [section]
            else:
                if not self.existsInGroup( section): # same melody and lyrics
                    sectionsWithThisName = self.groupsSimilarMelody[currMelodicStructLetter]
                    sectionsWithThisName.append(section)
    
    def existsInGroup(self, section):
    
        currMelodicStructLetter = section.melodicStructure[0]
        
        sectionsInGroup = self.groupsSimilarMelody[currMelodicStructLetter]
        for sectionInGr in sectionsInGroup:
            if sectionInGr.melodicStructure == section.melodicStructure and sectionInGr.lyricStructure == section.lyricStructure:
                    return 1
        return 0
    
    
    def getProbableLyricsForMelodicStructure(self, melodicStructure):
        
        '''B? -> B'''
         
        melodicStructLetter = melodicStructure[0]
        
        if melodicStructLetter not in self.groupsSimilarMelody:
            sys.exit("section {} not in metadata".format(melodicStructure))
        
        return self.groupsSimilarMelody[melodicStructLetter]


  
   ##################################################################################
    def printSectionsAndLyrics(self):
        '''
        utility method to print all lyrics that are read from symbTr
        '''
        for currSection in self.symbTrParser.sections:
    
            print '\n' + str(currSection.melodicStructure) + ' ' + str(currSection.lyricStructure)

            print currSection.lyrics
#             for word in  currSection[1]:
#                 print word.__str__().encode('utf-8','replace')
        

#     def serializePhonemesForSection(self, whichSection, outputFileName):
#         '''
#         list of all phonemes. print to file @param outputFileName
#         '''    
#         lyrics = self.getLyricsForSection(whichSection)
#         if not lyrics:
#             sys.exit("no lyrics")
#         
#         writeListToTextFile(lyrics.phonemesNetwork, None,  outputFileName )
#         return lyrics.phonemesNetwork
    
            
        
        
    def printSyllables(self, whichSection):
        '''
        debug: print syllables 
        '''
        
        lyrics = self.getLyricsForSection(whichSection)
        if not lyrics:
            sys.exit("no lyrics")
            
        lyrics.printSyllables
        
     
               


def loadMakamScore(pathToComposition):
    '''
    same as loadLyrics, but return MakamScore, so that all lyrics can be shown if needed
    '''
    Phonetizer.initLookupTable(False,  'grapheme2METUphonemeLookupTable')
    
    os.chdir(pathToComposition)

    pathTotxt = os.path.join(pathToComposition, glob.glob("*.txt")[0])
    
    listExtensions = [ "sectionsMetadata.json", "sectionsMetadata.tsv", "sectionsMetadata.txt"]
    sectionFiles = findFileByExtensions(pathToComposition, listExtensions)
    sectionFile = sectionFiles[0]
        
    pathToSectionTsv = os.path.join(pathToComposition, sectionFile)
    makamScore = MakamScore(pathTotxt, pathToSectionTsv )
    return makamScore


def loadMakamScore2(symbtrtxtURI, sectionMetadataURI):
    '''
    same as loadLyrics, but return MakamScore, so that all lyrics can be shown if needed
    '''
    Phonetizer.initLookupTable(False,  'grapheme2METUphonemeLookupTable')
    
    makamScore = MakamScore(symbtrtxtURI, sectionMetadataURI )
    return makamScore   

  
  
def printMakamScore(URI_dataset, workMBID):
        

        symbtr = compmusic.dunya.makam.get_symbtr(workMBID)
        compositionName = symbtr['name'] 

        
        ScoreURI = URI_dataset + compositionName + '/' + compositionName + '.txt'
        URISectionsMetadata = URI_dataset + compositionName + '/' + compositionName + '.sectionsMetadata.json'
        makamScore = loadMakamScore2(ScoreURI, URISectionsMetadata)
        makamScore.printSectionsAndLyrics()
        
        print '---------------------------------------------\n'
        
        ####### print groups with similar melody 
        print 'groupsSimilarMelody:'
        for group in makamScore.groupsSimilarMelody:
          print group + ':'
          for y in makamScore.groupsSimilarMelody[group]:
            print y
        print '---------------------------------------------\n'

        ####### print probable sections
        # print '---------------------------------------------\n'
        # sections = makamScore.getProbableLyricsForMelodicStructure('B1')
        # if sections:
        #     for section in sections:
        #         print section.__str__()
        
        # print '---------------------------------------------\n'
        # print '---------------------------------------------\n'
        # print '---------------------------------------------\n'     
           