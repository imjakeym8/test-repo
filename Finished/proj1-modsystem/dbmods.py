import pymongo
from pymongo import MongoClient
import discord

class XP:
    def __init__(self, mongo_client:MongoClient, user=None):
        self.client = mongo_client
        self.db = self.client.XP
        self.coll = self.db.mods
        if user:
            self.name = user.name #Discord function (username of user)
            self.display_name = user.display_name #Discord function (display name of user)
            self.discriminator = user.discriminator 

    def add(self, number:int):
        try:
            ans = self.coll.find_one({"handle":self.name},{"_id":0})

            if ans is None:
                return f"{self.name} not found."
            else:
                xp_count = ans["exp"] 
                xp_added = ans["added_exp"]

                new_xp = xp_count + number
                new_xp_added = xp_added + number
                self.coll.update_one({"handle":self.name},{"$set": {"exp":new_xp, "added_exp":new_xp_added}})

                return f"Added {number}. {self.name}'s EXP is now at {new_xp}."

        except Exception as e:
            return f"An error occured: {e}" 
    
    def remove(self, number:int):
        try:
            ans = self.coll.find_one({"handle":self.name},{"exp":1,"_id":0})

            if ans is None:
                return f"{self.name} not found."
            else:
                xp_count = ans["exp"]

                new_xp = xp_count - number
                self.coll.update_one({"handle":self.name},{"$set": {"exp":new_xp}})

                return f"Removed {number}. {self.name}'s EXP is now at {new_xp}."

        except Exception as e:
            return f"An error occured: {e}"

    def set(self, number:int):
        try:
            ans = self.coll.find_one({"handle":self.name},{"_id":0})

            if ans is None:
                return f"{self.name} not found."
            else:                
                self.coll.update_one({"handle":self.name},{"$set": {"exp":number,"added_exp":0}})
                return f"{self.name}'s EXP is now set to {number}."

        except Exception as e:
            return f"An error occured: {e}"

    def view(self):
        try:
            ans = self.coll.find_one({"handle":self.name},{"_id":0})

            if ans is None:
                return f"{self.name} not found."
            else:
                xp_count = ans["exp"]
                added_exp = ans["added_exp"]
                return f"{self.name}'s EXP is currently at {xp_count}. {added_exp} EXPs have been added in total."

        except Exception as e:
            return f"An error occured: {e}"
        
    def reset(self):
        try:
            ans = self.coll.find_one({"handle":self.name},{"_id":0})

            if ans is None:
                return f"{self.name} not found."
            else:
                self.coll.update_one({"handle":self.name},{"$set": {"exp":100,"added_exp":0}})
                return f"{self.name}'s EXP has been reset to 100."

        except Exception as e:
            return f"An error occured: {e}"
    
    def sort_winners(self,option):
        cursor = self.coll.find(filter=None,projection={"_id":False},sort=[("exp",pymongo.DESCENDING)],limit=10)
        
        if option == "a":
            sorted_handle = [ document["handle"] for document in cursor ]
            return sorted_handle 
        
        if option == "b":
            sorted_exp = [ document["added_exp"] for document in cursor ]
            return sorted_exp
    
    def register(self):
        try:
            ans = self.coll.find_one({"handle":self.name})
            if ans is None:
                self.coll.insert_one({"name":self.display_name,"handle":self.name, "exp":100, "added_exp":0})
                return f"{self.name} has successfully been added to the database."
            else:
                return f"{self.name} already exists in the database."
            
        except Exception as e:
            return f"An error occured: {e}"

                