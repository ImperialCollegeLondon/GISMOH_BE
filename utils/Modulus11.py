'''
Created on 26 Nov 2012

@author: cpowell
'''
import math

class Mod11:
    @staticmethod
    def calculate(number):
        
        if isinstance(number, str):
            number = int(number)
        
        num = number
        mod_sum = 0
        i = 2
        while num != 0:
            mod_sum += (num % 10) * i 
            num = math.floor(num / 10)
            i += 1
            
        mod_r = mod_sum % 11
        mod_r = 11 - mod_r
        
        return int(mod_r) if mod_r < 10 else 'X' 
            
            
    @staticmethod
    def check (number):
        if isinstance(number, str):
            if number[len(number) - 1] == 'X':
                n = number[:-1]
                num = int(n)
                prov_cd = 'X'
            else:
                number = int(number)
                prov_cd = number % 10 
                num = math.floor(number /10)
        else :    
            prov_cd = number % 10 
            num = math.floor(number /10)
            
        act_cd = Mod11.calculate(num)
        
        return act_cd == prov_cd
        
    