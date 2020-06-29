from collections import defaultdict
import sys
class Solution:
    '''
    @param source : A string
    @param target: A string
    @return: A string denote the minimum window, return "" if there is no such a string
    '''
    def minWindow(self, source , target):
        # write your code here
        if source is None or target is None:
            return None
        
        if not source or not target:
            return ""
        
        start, end = 0, 0    
        minimumLength, windowSubstring = sys.maxsize, ""
        sourceHashmap = defaultdict(int)
        targetHashmap = defaultdict(int)
        
        for ch in target:
            targetHashmap[ch] += 1

        for start in range(len(source)):
            while end < len(source) and not self.isSourceHashMapContainsTarget(sourceHashmap, targetHashmap):
                print(start, end, source[end])
                sourceHashmap[source[end]] += 1
                end += 1

                
                
            if self.isSourceHashMapContainsTarget(sourceHashmap, targetHashmap) and end - start < minimumLength:
                minimumLength = end - start
                windowSubstring = source[start:end]
            
            sourceHashmap[source[start]] -= 1
            if sourceHashmap[source[start]] == 0:
                del sourceHashmap[source[start]]

        return windowSubstring
        
        
    def isSourceHashMapContainsTarget(self, sourceHashmap, targetHashmap):
        for ch in targetHashmap:
            if sourceHashmap[ch] < targetHashmap[ch]:
                return False
          
        return True
a=Solution()
src='123loveurdfiosjdfgsjgsoivh98wehfskjdviakdhflosdfzxccvzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzkkkkkkkkkkkkkkkkkkkkkkkkkkvvvvvvvvvvvvvvvvvvvvvvvvvrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttllllllllllllllvesjdfhvndxjyou123loveurdfiosjdfgsjgsoivh98wehfskjdviakdhflosdfzxccvzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzkkkkkkkkkkkkkkkkkkkkkkkkkkvvvvvvvvvvvvvvvvvvvvvvvvvrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttllllllllllllllvesjdfhvndxjyou'
target='loveyu'
r=a.minWindow(src,target)
