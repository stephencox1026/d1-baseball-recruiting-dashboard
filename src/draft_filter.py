"""
MLB Draft Filter Module for D1 Baseball Recruitment Dashboard

Filters out players who have already been drafted in the MLB Draft.
Uses complete 2025 MLB Draft data provided by user.
"""

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CURRENT_SEASON, CACHE_DIR
from src.utils import ensure_directories, save_dataframe


class DraftFilter:
    """
    Filters out MLB-drafted players from recruitment candidates.
    Uses complete 2025 MLB Draft data (615 picks).
    """
    
    def __init__(self):
        self.drafted_players = pd.DataFrame()
        # Cover recent drafts - players drafted in these years should be excluded
        self.draft_years = [2022, 2023, 2024, 2025]
        ensure_directories()
    
    def fetch_draft_data(self) -> pd.DataFrame:
        """
        Get MLB Draft data - uses comprehensive 2025 draft list.
        
        Returns:
            DataFrame with drafted player information
        """
        print("Loading complete 2025 MLB Draft data (615 picks)...")
        self._create_complete_draft_list()
        return self.drafted_players
    
    def _create_complete_draft_list(self):
        """
        Complete list of all college players from 2025 MLB Draft.
        Extracted from Baseball America draft results.
        """
        drafted_2025 = [
            # Round 1
            {'name': 'Tyler Bremner', 'school': 'UC Santa Barbara', 'round': 1},
            {'name': 'Kade Anderson', 'school': 'LSU', 'round': 1},
            {'name': 'Liam Doyle', 'school': 'Tennessee', 'round': 1},
            {'name': 'Aiva Arquette', 'school': 'Oregon State', 'round': 1},
            {'name': 'Jamie Arnold', 'school': 'Florida State', 'round': 1},
            {'name': 'Gavin Kilen', 'school': 'Tennessee', 'round': 1},
            {'name': 'Kyson Witherspoon', 'school': 'Oklahoma', 'round': 1},
            {'name': 'Marek Houston', 'school': 'Wake Forest', 'round': 1},
            {'name': 'Ethan Conrad', 'school': 'Wake Forest', 'round': 1},
            {'name': 'Ike Irish', 'school': 'Auburn', 'round': 1},
            {'name': 'Andrew Fischer', 'school': 'Tennessee', 'round': 1},
            {'name': 'Mitch Voit', 'school': 'Michigan', 'round': 1},
            {'name': 'Zach Root', 'school': 'Arkansas', 'round': 1},
            {'name': 'Patrick Forbes', 'school': 'Louisville', 'round': 1},
            {'name': 'Caden Bodine', 'school': 'Coastal Carolina', 'round': 1},
            {'name': 'Wehiwa Aloy', 'school': 'Arkansas', 'round': 1},
            {'name': 'Marcus Phillips', 'school': 'Tennessee', 'round': 1},
            {'name': 'Luke Stevenson', 'school': 'North Carolina', 'round': 1},
            {'name': 'Riley Quick', 'school': 'Alabama', 'round': 1},
            {'name': 'Jace LaViolette', 'school': 'Texas A&M', 'round': 1},
            {'name': 'Charles Davalan', 'school': 'Arkansas', 'round': 1},
            {'name': 'Brendan Summerhill', 'school': 'Arizona', 'round': 1},
            {'name': 'Cam Cannarella', 'school': 'Clemson', 'round': 1},
            
            # Round 2
            {'name': 'J.B. Middleton', 'school': 'Southern Mississippi', 'round': 2},
            {'name': 'Brandon Compton', 'school': 'Arizona State', 'round': 2},
            {'name': 'Chase Shores', 'school': 'LSU', 'round': 2},
            {'name': 'Devin Taylor', 'school': 'Indiana', 'round': 2},
            {'name': 'Ethan Petry', 'school': 'South Carolina', 'round': 2},
            {'name': 'A.J. Russell', 'school': 'Tennessee', 'round': 2},
            {'name': 'Kane Kepley', 'school': 'North Carolina', 'round': 2},
            {'name': 'Joseph Dzierwa', 'school': 'Michigan State', 'round': 2},
            {'name': 'JD Thompson', 'school': 'Vanderbilt', 'round': 2},
            {'name': 'Alex Lodise', 'school': 'Florida State', 'round': 2},
            {'name': 'Michael Lombardi', 'school': 'Tulane', 'round': 2},
            {'name': 'Malachi Witherspoon', 'school': 'Oklahoma', 'round': 2},
            {'name': 'Cade Obermueller', 'school': 'Iowa', 'round': 2},
            {'name': 'Dean Curley', 'school': 'Tennessee', 'round': 2},
            {'name': 'Cam Leiter', 'school': 'Florida State', 'round': 2},
            {'name': 'Aaron Walton', 'school': 'Arizona', 'round': 2},
            {'name': 'J.T. Quinn', 'school': 'Georgia', 'round': 2},
            {'name': 'Justin Lamkin', 'school': 'Texas A&M', 'round': 2},
            {'name': 'Tanner Franklin', 'school': 'Tennessee', 'round': 2},
            {'name': 'Murf Gray', 'school': 'Fresno State', 'round': 2},
            {'name': 'Max Belyeu', 'school': 'Texas', 'round': 2},
            {'name': 'Henry Godbout', 'school': 'Virginia', 'round': 2},
            
            # Round 3
            {'name': 'Kyle Lodise', 'school': 'Georgia Tech', 'round': 3},
            {'name': 'Ethan Hedges', 'school': 'USC', 'round': 3},
            {'name': 'Max Williams', 'school': 'Florida State', 'round': 3},
            {'name': 'Jake Cook', 'school': 'Southern Mississippi', 'round': 3},
            {'name': 'Easton Carmichael', 'school': 'Oklahoma', 'round': 3},
            {'name': 'Mason Morris', 'school': 'Ole Miss', 'round': 3},
            {'name': 'Trevor Cohen', 'school': 'Rutgers', 'round': 3},
            {'name': 'Anthony Eyanson', 'school': 'LSU', 'round': 3},
            {'name': 'James Ellwanger', 'school': 'Dallas Baptist', 'round': 3},
            {'name': 'Jack Gurevitch', 'school': 'University Of San Diego', 'round': 3},
            {'name': 'Dominick Reid', 'school': 'Abilene Christian', 'round': 3},
            {'name': 'Griffin Hugus', 'school': 'Miami', 'round': 3},
            {'name': 'Brian Curley', 'school': 'Georgia', 'round': 3},
            {'name': 'RJ Austin', 'school': 'Vanderbilt', 'round': 3},
            {'name': 'Jacob Morrison', 'school': 'Coastal Carolina', 'round': 3},
            {'name': 'Ethan Frey', 'school': 'LSU', 'round': 3},
            {'name': 'Cody Miller', 'school': 'East Tennessee State', 'round': 3},
            {'name': 'Ben Jacobs', 'school': 'Arizona State', 'round': 3},
            {'name': 'Ryan Wideman', 'school': 'Western Kentucky', 'round': 3},
            {'name': 'Cody Bowker', 'school': 'Vanderbilt', 'round': 3},
            {'name': 'Nolan Schubart', 'school': 'Oklahoma State', 'round': 3},
            {'name': 'Antonio Jimenez', 'school': 'Central Florida', 'round': 3},
            {'name': 'Kaeden Kent', 'school': 'Texas A&M', 'round': 3},
            {'name': 'Landyn Vidourek', 'school': 'Cincinnati', 'round': 3},
            {'name': 'Nate Snead', 'school': 'Tennessee', 'round': 3},
            
            # Round 4
            {'name': 'Riley Kelly', 'school': 'UC Irvine', 'round': 4},
            {'name': 'Drew Faurot', 'school': 'Florida State', 'round': 4},
            {'name': 'Jake Munroe', 'school': 'Louisville', 'round': 4},
            {'name': 'Gavin Turley', 'school': 'Oregon State', 'round': 4},
            {'name': 'Micah Bucknam', 'school': 'Dallas Baptist', 'round': 4},
            {'name': 'Mason Neville', 'school': 'Oregon', 'round': 4},
            {'name': 'Mason McConnaughey', 'school': 'Nebraska', 'round': 4},
            {'name': 'Lorenzo Meola', 'school': 'Stetson', 'round': 4},
            {'name': 'Dominic Fritton', 'school': 'NC State', 'round': 4},
            {'name': 'Mason White', 'school': 'Arizona', 'round': 4},
            {'name': 'Jason Reitz', 'school': 'Oregon', 'round': 4},
            {'name': 'Cade Crossland', 'school': 'Oklahoma', 'round': 4},
            {'name': 'Mason Peters', 'school': 'Dallas Baptist', 'round': 4},
            {'name': 'Colin Yeaman', 'school': 'UC Irvine', 'round': 4},
            {'name': 'Nick Monistere', 'school': 'Southern Mississippi', 'round': 4},
            {'name': 'Nolan Sailors', 'school': 'Creighton', 'round': 4},
            {'name': 'Caleb Leys', 'school': 'Maine', 'round': 4},
            {'name': 'Michael Salina', 'school': 'St. Bonaventure', 'round': 4},
            {'name': 'Sean Youngerman', 'school': 'Oklahoma State', 'round': 4},
            {'name': 'Luke Hill', 'school': 'Ole Miss', 'round': 4},
            {'name': 'Pico Kohn', 'school': 'Mississippi State', 'round': 4},
            {'name': 'Dixon Williams', 'school': 'East Carolina', 'round': 4},
            
            # Round 5
            {'name': 'Gabe Davis', 'school': 'Oklahoma State', 'round': 5},
            {'name': 'Cameron Nelson', 'school': 'Wake Forest', 'round': 5},
            {'name': 'Chris Arroyo', 'school': 'Virginia', 'round': 5},
            {'name': 'Zane Taylor', 'school': 'UNC Wilmington', 'round': 5},
            {'name': 'Adonys Guzman', 'school': 'Arizona', 'round': 5},
            {'name': 'Ben Abeldt', 'school': 'TCU', 'round': 5},
            {'name': 'James Quinn-Irons', 'school': 'George Mason', 'round': 5},
            {'name': 'Christian Foutch', 'school': 'Arkansas', 'round': 5},
            {'name': 'Ethan Young', 'school': 'East Carolina', 'round': 5},
            {'name': 'Kade Snell', 'school': 'Alabama', 'round': 5},
            {'name': 'Korbyn Dickerson', 'school': 'Indiana', 'round': 5},
            {'name': 'Nathan Hall', 'school': 'South Carolina', 'round': 5},
            {'name': 'Sean Episcope', 'school': 'Princeton', 'round': 5},
            {'name': 'Nick Potter', 'school': 'Wichita State', 'round': 5},
            {'name': 'Aiden Jimenez', 'school': 'Arkansas', 'round': 5},
            {'name': 'Gabe Craig', 'school': 'Baylor', 'round': 5},
            {'name': 'Riley Nelson', 'school': 'Vanderbilt', 'round': 5},
            {'name': 'Peyton Prescott', 'school': 'Florida State', 'round': 5},
            {'name': 'Core Jackson', 'school': 'Utah', 'round': 5},
            {'name': 'Davion Hickson', 'school': 'Rice', 'round': 5},
            
            # Round 6
            {'name': 'Colby Shelton', 'school': 'Florida', 'round': 6},
            {'name': 'Matt Klein', 'school': 'Louisville', 'round': 6},
            {'name': 'Joey Volini', 'school': 'Florida State', 'round': 6},
            {'name': 'Grant Richardson', 'school': 'Grand Canyon', 'round': 6},
            {'name': 'Boston Smith', 'school': 'Wright State', 'round': 6},
            {'name': 'Eric Snow', 'school': 'Auburn', 'round': 6},
            {'name': 'Jack Anker', 'school': 'Fresno State', 'round': 6},
            {'name': 'Braden Osbolt', 'school': 'Kennesaw State', 'round': 6},
            {'name': 'Jordan Gottesman', 'school': 'Northeastern', 'round': 6},
            {'name': 'Aidan Haugh', 'school': 'North Carolina', 'round': 6},
            {'name': 'Leighton Finley', 'school': 'Georgia', 'round': 6},
            {'name': 'Matthew Miura', 'school': 'Hawaii', 'round': 6},
            {'name': 'Lucas Kelly', 'school': 'Arizona State', 'round': 6},
            {'name': 'Sawyer Hawks', 'school': 'Vanderbilt', 'round': 6},
            {'name': 'Caden Hunter', 'school': 'USC', 'round': 6},
            {'name': 'Daniel Dickinson', 'school': 'LSU', 'round': 6},
            {'name': 'Gabel Pentecost', 'school': 'Taylor University', 'round': 6},
            {'name': 'Landon Beidelschies', 'school': 'Arkansas', 'round': 6},
            {'name': 'Tyriq Kemp', 'school': 'Baylor', 'round': 6},
            {'name': 'Grayson Grinsell', 'school': 'Oregon', 'round': 6},
            {'name': 'Jaxon Dalena', 'school': 'Shippensburg', 'round': 6},
            {'name': 'James Tallon', 'school': 'Duke', 'round': 6},
            {'name': 'Nelson Keljo', 'school': 'Oregon State', 'round': 6},
            {'name': 'Rory Fox', 'school': 'Notre Dame', 'round': 6},
            
            # Round 7
            {'name': 'Anthony DePino', 'school': 'Rhode Island', 'round': 7},
            {'name': 'Antoine Jean', 'school': 'Houston', 'round': 7},
            {'name': 'Jake Clemente', 'school': 'Florida', 'round': 7},
            {'name': 'Lucas Mahlstedt', 'school': 'Clemson', 'round': 7},
            {'name': 'Logan Sauve', 'school': 'West Virginia', 'round': 7},
            {'name': 'Julian Tonghini', 'school': 'Arizona', 'round': 7},
            {'name': 'Dylan Watts', 'school': 'Auburn', 'round': 7},
            {'name': 'Brent Iredale', 'school': 'Arkansas', 'round': 7},
            {'name': 'Justin Henschel', 'school': 'Florida Gulf Coast', 'round': 7},
            {'name': 'Paxton Kling', 'school': 'Penn State', 'round': 7},
            {'name': 'Cam Maldonado', 'school': 'Northeastern', 'round': 7},
            {'name': 'Myles Patton', 'school': 'Texas A&M', 'round': 7},
            {'name': 'Jacob McCombs', 'school': 'UC Irvine', 'round': 7},
            {'name': 'Payton Graham', 'school': 'Gonzaga', 'round': 7},
            {'name': 'Pierce Coppola', 'school': 'Florida', 'round': 7},
            {'name': 'Colton Shaw', 'school': 'Yale', 'round': 7},
            {'name': 'Joe Ariola', 'school': 'Wake Forest', 'round': 7},
            {'name': 'Hunter Allen', 'school': 'Ashland', 'round': 7},
            {'name': 'Josiah Ragsdale', 'school': 'Boston College', 'round': 7},
            {'name': 'Zach Royse', 'school': 'UTSA', 'round': 7},
            {'name': 'Bryson Dudley', 'school': 'Texas State', 'round': 7},
            {'name': 'Kerrington Cross', 'school': 'Cincinnati', 'round': 7},
            {'name': 'Will McCausland', 'school': 'Ole Miss', 'round': 7},
            {'name': 'Cam Tilly', 'school': 'Auburn', 'round': 7},
            {'name': 'Richie Bonomolo', 'school': 'Alabama', 'round': 7},
            {'name': 'Mason Estrada', 'school': 'MIT', 'round': 7},
            
            # Round 8
            {'name': 'Blaine Wynk', 'school': 'Ohio State', 'round': 8},
            {'name': 'Tanner Thach', 'school': 'UNC Wilmington', 'round': 8},
            {'name': 'Emilio Barreras', 'school': 'Grand Canyon', 'round': 8},
            {'name': 'Isaiah Jackson', 'school': 'Arizona State', 'round': 8},
            {'name': 'Corey Braun', 'school': 'South Florida', 'round': 8},
            {'name': 'Riley Maddox', 'school': 'Ole Miss', 'round': 8},
            {'name': 'Danny Thompson', 'school': 'UNC Greensboro', 'round': 8},
            {'name': 'Josh Tate', 'school': 'Georgia Southern', 'round': 8},
            {'name': 'Kyle McCoy', 'school': 'Maryland', 'round': 8},
            {'name': 'Evan Siary', 'school': 'Mississippi State', 'round': 8},
            {'name': 'Ben Bybee', 'school': 'Arkansas', 'round': 8},
            {'name': 'Aidan Cremarosa', 'school': 'Fresno State', 'round': 8},
            {'name': 'Dylan Brown', 'school': 'Old Dominion', 'round': 8},
            {'name': 'Ryan Sprock', 'school': 'Elon', 'round': 8},
            {'name': 'Ryan Weingartner', 'school': 'Penn State', 'round': 8},
            {'name': 'Jake Knapp', 'school': 'North Carolina', 'round': 8},
            {'name': 'Danny Macchiarola', 'school': 'Holy Cross', 'round': 8},
            {'name': 'Jack Martinez', 'school': 'Arizona State', 'round': 8},
            {'name': 'Kailen Hamson', 'school': 'Cumberlands', 'round': 8},
            {'name': 'Kyle Walker', 'school': 'Arizona State', 'round': 8},
            {'name': 'Carter Lovasz', 'school': 'William & Mary', 'round': 8},
            {'name': 'Brooks Bryan', 'school': 'Troy', 'round': 8},
            {'name': 'Nick Dumesnil', 'school': 'California Baptist', 'round': 8},
            {'name': 'James Hitt', 'school': 'Oklahoma', 'round': 8},
            {'name': 'Brian Walters', 'school': 'Miami', 'round': 8},
            {'name': 'Anthony Martinez', 'school': 'UC Irvine', 'round': 8},
            {'name': 'Mac Heuer', 'school': 'Texas Tech', 'round': 8},
            {'name': 'Jack O\'Connor', 'school': 'Virginia', 'round': 8},
            
            # Round 9
            {'name': 'Riley Eikhoff', 'school': 'Coastal Carolina', 'round': 9},
            {'name': 'Zach Rogacki', 'school': 'Binghamton', 'round': 9},
            {'name': 'Kaiden Wilson', 'school': 'Texas A&M', 'round': 9},
            {'name': 'Slate Alford', 'school': 'Georgia', 'round': 9},
            {'name': 'Daniel Bucciero', 'school': 'Fordham', 'round': 9},
            {'name': 'Wyatt Henseler', 'school': 'Texas A&M', 'round': 9},
            {'name': 'Karson Ligon', 'school': 'Mississippi State', 'round': 9},
            {'name': 'Jared Jones', 'school': 'LSU', 'round': 9},
            {'name': 'Kien Vu', 'school': 'Arizona State', 'round': 9},
            {'name': 'Owen Proksch', 'school': 'Duke', 'round': 9},
            {'name': 'Mason Nichols', 'school': 'Ole Miss', 'round': 9},
            {'name': 'Jacob Mayers', 'school': 'LSU', 'round': 9},
            {'name': 'Justin Mitrovich', 'school': 'Elon', 'round': 9},
            {'name': 'Michael Dattalo', 'school': 'Dallas Baptist', 'round': 9},
            {'name': 'Colton Book', 'school': 'Saint Joseph\'s', 'round': 9},
            {'name': 'Jackson Steensma', 'school': 'Appalachian State', 'round': 9},
            {'name': 'Wallace Clark', 'school': 'Duke', 'round': 9},
            {'name': 'Andrew Healy', 'school': 'Duke', 'round': 9},
            {'name': 'Kellan Oakes', 'school': 'Oregon State', 'round': 9},
            {'name': 'Logan Braunschweig', 'school': 'UAB', 'round': 9},
            {'name': 'Shane Van Dam', 'school': 'NC State', 'round': 9},
            {'name': 'Will Koger', 'school': 'Arizona State', 'round': 9},
            {'name': 'Ryan Prager', 'school': 'Texas A&M', 'round': 9},
            {'name': 'Blake Gillespie', 'school': 'UNC Charlotte', 'round': 9},
            {'name': 'Conner O\'Neal', 'school': 'Southeastern Louisiana', 'round': 9},
            
            # Round 10
            {'name': 'Dan Wright', 'school': 'Iowa', 'round': 10},
            {'name': 'Austin Newton', 'school': 'South Florida', 'round': 10},
            {'name': 'Jake McCutcheon', 'school': 'Missouri State', 'round': 10},
            {'name': 'Nick Rodriguez', 'school': 'Missouri State', 'round': 10},
            {'name': 'Samuel Dutton', 'school': 'Auburn', 'round': 10},
            {'name': 'Hunter Hines', 'school': 'Mississippi State', 'round': 10},
            {'name': 'Austin Smith', 'school': 'San Diego', 'round': 10},
            {'name': 'Matt King', 'school': 'Arizona State', 'round': 10},
            {'name': 'Ty Doucette', 'school': 'Rutgers', 'round': 10},
            {'name': 'J.D. McReynolds', 'school': 'Central Missouri', 'round': 10},
            {'name': 'Isaiah Barkett', 'school': 'Stetson', 'round': 10},
            {'name': 'Trendan Parish', 'school': 'Texas Tech', 'round': 10},
            {'name': 'Maximus Martin', 'school': 'Kansas State', 'round': 10},
            {'name': 'Shai Robinson', 'school': 'Illinois State', 'round': 10},
            {'name': 'Ty Van Dyke', 'school': 'Stetson', 'round': 10},
            {'name': 'Justin Stransky', 'school': 'Fresno State', 'round': 10},
            {'name': 'Isaac Lyon', 'school': 'Grand Canyon', 'round': 10},
            {'name': 'Brady Counsell', 'school': 'Kansas', 'round': 10},
            {'name': 'Dalton Neuschwander', 'school': 'West Florida', 'round': 10},
            {'name': 'Braylon Owens', 'school': 'UTSA', 'round': 10},
            {'name': 'Zach Daudet', 'school': 'Cal Poly', 'round': 10},
            {'name': 'Kade Woods', 'school': 'LSU', 'round': 10},
            {'name': 'Max Martin', 'school': 'UC Irvine', 'round': 10},
            {'name': 'Edian Espinal', 'school': 'Central Florida', 'round': 10},
            {'name': 'Justin DeCriscio', 'school': 'NC State', 'round': 10},
            {'name': 'Cole Gilley', 'school': 'Indiana', 'round': 10},
            {'name': 'Harrison Bodendorf', 'school': 'Oklahoma State', 'round': 10},
            {'name': 'Tyler McLoughlin', 'school': 'Georgia', 'round': 10},
            {'name': 'Connor McGinnis', 'school': 'Houston', 'round': 10},
            {'name': 'Jacob Frost', 'school': 'Kansas State', 'round': 10},
            
            # Round 11
            {'name': 'Zach Harris', 'school': 'Georgia', 'round': 11},
            {'name': 'Jadon Williamson', 'school': 'Lewis-Clark State', 'round': 11},
            {'name': 'Alton Davis', 'school': 'Georgia', 'round': 11},
            {'name': 'Bobby Boser', 'school': 'Florida', 'round': 11},
            {'name': 'Jack Moroknek', 'school': 'Butler', 'round': 11},
            {'name': 'Jared Spencer', 'school': 'Texas', 'round': 11},
            {'name': 'Dylan Palmer', 'school': 'Hofstra', 'round': 11},
            {'name': 'Jake Brink', 'school': 'College of Charleston', 'round': 11},
            {'name': 'Luke Jackson', 'school': 'Texas A&M', 'round': 11},
            {'name': 'Ryan Daniels', 'school': 'Connecticut', 'round': 11},
            {'name': 'Jalin Flores', 'school': 'Texas', 'round': 11},
            {'name': 'Eli Jerzembeck', 'school': 'South Carolina', 'round': 11},
            {'name': 'Dusty Revis', 'school': 'Western Carolina', 'round': 11},
            {'name': 'Luke Dotson', 'school': 'Mississippi State', 'round': 11},
            {'name': 'Holden deJong', 'school': 'NJIT', 'round': 11},
            {'name': 'Justin Thomas', 'school': 'Arkansas', 'round': 11},
            {'name': 'Colin Daniel', 'school': 'UAB', 'round': 11},
            {'name': 'Hunter Alberini', 'school': 'Arizona', 'round': 11},
            {'name': 'Ben Grable', 'school': 'Indiana', 'round': 11},
            {'name': 'Dylan Tate', 'school': 'Oklahoma', 'round': 11},
            
            # Round 12
            {'name': 'Ely Brown', 'school': 'Mercer', 'round': 12},
            {'name': 'Brady Parker', 'school': 'Houston-Victoria', 'round': 12},
            {'name': 'Wilson Weber', 'school': 'Oregon State', 'round': 12},
            {'name': 'Ben Moore', 'school': 'Old Dominion', 'round': 12},
            {'name': 'Cameron Keshock', 'school': 'Samford', 'round': 12},
            {'name': 'Carson Latimer', 'school': 'Sacramento State', 'round': 12},
            {'name': 'Cody Delvecchio', 'school': 'UCLA', 'round': 12},
            {'name': 'Brady Jones', 'school': 'Georgia Tech', 'round': 12},
            {'name': 'Ethan Walker', 'school': 'Kentucky', 'round': 12},
            {'name': 'Kolten Smith', 'school': 'Georgia', 'round': 12},
            {'name': 'Kaden Echeman', 'school': 'Northern Kentucky', 'round': 12},
            {'name': 'Connor Spencer', 'school': 'Ole Miss', 'round': 12},
            {'name': 'Grant Jay', 'school': 'Dallas Baptist', 'round': 12},
            {'name': 'Tayler Montiel', 'school': 'Tulane', 'round': 12},
            {'name': 'Jay Woolfolk', 'school': 'Virginia', 'round': 12},
            {'name': 'Matthew Hoskins', 'school': 'Georgia', 'round': 12},
            {'name': 'George Bilecki', 'school': 'Lewis', 'round': 12},
            {'name': 'Tyler Bowen', 'school': 'Lander', 'round': 12},
            {'name': 'Ryan DeSanto', 'school': 'Penn State', 'round': 12},
            {'name': 'Truman Pauley', 'school': 'Harvard', 'round': 12},
            {'name': 'Camden Troyer', 'school': 'Liberty', 'round': 12},
            {'name': 'Logan Lunceford', 'school': 'Wake Forest', 'round': 12},
            
            # Round 13
            {'name': 'Rylan Galvan', 'school': 'Texas', 'round': 13},
            {'name': 'Chase Renner', 'school': 'Penn State', 'round': 13},
            {'name': 'Bryan Arendt', 'school': 'UNC Wilmington', 'round': 13},
            {'name': 'Tucker Biven', 'school': 'Louisville', 'round': 13},
            {'name': 'Trace Baker', 'school': 'UNC Wilmington', 'round': 13},
            {'name': 'Dylan Mathiesen', 'school': 'Liberty', 'round': 13},
            {'name': 'Brady Afthim', 'school': 'Connecticut', 'round': 13},
            {'name': 'Broedy Poppell', 'school': 'Florida A&M', 'round': 13},
            {'name': 'Jack Winnay', 'school': 'Wake Forest', 'round': 13},
            {'name': 'Callan Fang', 'school': 'Harvard', 'round': 13},
            {'name': 'Jake Shelagowski', 'school': 'Saginaw Valley State', 'round': 13},
            {'name': 'Nathan Williams', 'school': 'Mississippi State', 'round': 13},
            {'name': 'Aiden Taurek', 'school': 'Saint Mary\'s', 'round': 13},
            {'name': 'Alex Galvan', 'school': 'Central Florida', 'round': 13},
            {'name': 'Brayden Smith', 'school': 'Oklahoma State', 'round': 13},
            {'name': 'Aubrey Smith', 'school': 'UNC Wilmington', 'round': 13},
            {'name': 'Logan Forsythe', 'school': 'Louisiana Tech', 'round': 13},
            {'name': 'Jack Goodman', 'school': 'Northeastern', 'round': 13},
            {'name': 'Dylan Grego', 'school': 'Ball State', 'round': 13},
            {'name': 'Aaron Savary', 'school': 'Iowa', 'round': 13},
            {'name': 'Frank Camarillo', 'school': 'UC Santa Barbara', 'round': 13},
            {'name': 'Kyle West', 'school': 'West Virginia', 'round': 13},
            {'name': 'Robby Porco', 'school': 'West Virginia', 'round': 13},
            
            # Round 14
            {'name': 'Max Banks', 'school': 'Washington', 'round': 14},
            {'name': 'Luke Broderick', 'school': 'Nebraska', 'round': 14},
            {'name': 'Carson Laws', 'school': 'Texas State', 'round': 14},
            {'name': 'Griffin Kirn', 'school': 'West Virginia', 'round': 14},
            {'name': 'NIck Hollifield', 'school': 'UAB', 'round': 14},
            {'name': 'Noah Palmese', 'school': 'Webber International', 'round': 14},
            {'name': 'Bryce Archie', 'school': 'South Florida', 'round': 14},
            {'name': 'Trey Seeley', 'school': 'Hope International', 'round': 14},
            {'name': 'Jacob Hartlaub', 'school': 'Ball State', 'round': 14},
            {'name': 'Carter Rasmussen', 'school': 'Wofford', 'round': 14},
            {'name': 'Merit Jones', 'school': 'Utah', 'round': 14},
            {'name': 'Anthony Watts', 'school': 'Iowa', 'round': 14},
            {'name': 'Luke Heyman', 'school': 'Florida', 'round': 14},
            {'name': 'Garrett Langrell', 'school': 'Creighton', 'round': 14},
            {'name': 'Riley Stanford', 'school': 'Georgia Tech', 'round': 14},
            {'name': 'Jason Gilman', 'school': 'Kean', 'round': 14},
            {'name': 'Jonathan Stevens', 'school': 'Alabama', 'round': 14},
            {'name': 'Alex Breckheimer', 'school': 'Kansas', 'round': 14},
            {'name': 'Riely Hunsaker', 'school': 'Lamar', 'round': 14},
            {'name': 'Casey Hintz', 'school': 'Arizona', 'round': 14},
            {'name': 'Collin Rothermel', 'school': 'Jacksonville', 'round': 14},
            {'name': 'Josh Wakefield', 'school': 'Grand Canyon', 'round': 14},
            {'name': 'Mathieu Curtis', 'school': 'Virginia Tech', 'round': 14},
            {'name': 'Beau Ankeney', 'school': 'Loyola Marymount', 'round': 14},
            {'name': 'Clay Edmondson', 'school': 'UNC Asheville', 'round': 14},
            {'name': 'Jonathan Gonzalez', 'school': 'Stetson', 'round': 14},
            {'name': 'Anthony Silva', 'school': 'TCU', 'round': 14},
            {'name': 'Brennan Stuprich', 'school': 'Southeastern Louisiana', 'round': 14},
            {'name': 'Davis Chastain', 'school': 'Georgia', 'round': 14},
            
            # Round 15
            {'name': 'Caedmon Parker', 'school': 'TCU', 'round': 15},
            {'name': 'Dylan Crooks', 'school': 'Oklahoma', 'round': 15},
            {'name': 'Josh Hogue', 'school': 'NC State', 'round': 15},
            {'name': 'Jacob Walsh', 'school': 'Oregon', 'round': 15},
            {'name': 'Casey Jake', 'school': 'Kent State', 'round': 15},
            {'name': 'Andrew Shaffner', 'school': 'NC State', 'round': 15},
            {'name': 'Luke Hanson', 'school': 'Virginia', 'round': 15},
            {'name': 'Damian Bravo', 'school': 'Texas Tech', 'round': 15},
            {'name': 'Skylar King', 'school': 'West Virginia', 'round': 15},
            {'name': 'Reed Moring', 'school': 'UC Santa Barbara', 'round': 15},
            {'name': 'Trevor Haskins', 'school': 'Stanford', 'round': 15},
            {'name': 'Noah Edders', 'school': 'Troy', 'round': 15},
            {'name': 'Brayden Corn', 'school': 'Western Carolina', 'round': 15},
            {'name': 'Hayden Murphy', 'school': 'Auburn', 'round': 15},
            {'name': 'DJ Newman', 'school': 'Bowling Green', 'round': 15},
            {'name': 'Dallas Macias', 'school': 'Oregon State', 'round': 15},
            {'name': 'Connor Rasmussen', 'school': 'Tulane', 'round': 15},
            {'name': 'Charlie Christensen', 'school': 'Central Arkansas', 'round': 15},
            {'name': 'Ryan Reed', 'school': 'Pittsburgh', 'round': 15},
            {'name': 'Jacob Pruitt', 'school': 'Mississippi State', 'round': 15},
            {'name': 'Evan Chrest', 'school': 'Florida State', 'round': 15},
            {'name': 'Conner Ware', 'school': 'LSU', 'round': 15},
            {'name': 'Jack Cebert', 'school': 'Texas Tech', 'round': 15},
            {'name': 'Matt Lanzendorfer', 'school': 'Virginia', 'round': 15},
            
            # Round 16
            {'name': 'Kaleb Freeman', 'school': 'Georgia State', 'round': 16},
            {'name': 'Seth Clausen', 'school': 'Minnesota', 'round': 16},
            {'name': 'RJ Shunck', 'school': 'Toledo', 'round': 16},
            {'name': 'Gage Harrelson', 'school': 'Florida State', 'round': 16},
            {'name': 'Jackson Phipps', 'school': 'Jacksonville State', 'round': 16},
            {'name': 'Levi Huesman', 'school': 'Vanderbilt', 'round': 16},
            {'name': 'Jaxson West', 'school': 'Florida State', 'round': 16},
            {'name': 'Eddie King', 'school': 'Louisville', 'round': 16},
            {'name': 'Maison Martinez', 'school': 'Florida State', 'round': 16},
            {'name': 'Chase Call', 'school': 'UC Irvine', 'round': 16},
            {'name': 'Joe Ruzicka', 'school': 'Belmont', 'round': 16},
            {'name': 'Cardell Thibodeaux', 'school': 'Southern', 'round': 16},
            {'name': 'Logan Dawson', 'school': 'Eastern HS', 'round': 16},
            {'name': 'Luke Fernandez', 'school': 'Wallace State', 'round': 16},
            {'name': 'Zack Mack', 'school': 'Loyola Marymount', 'round': 16},
            {'name': 'Jackson Lovich', 'school': 'Missouri', 'round': 16},
            {'name': 'AJ Soldra', 'school': 'Seton Hall', 'round': 16},
            
            # Round 17
            {'name': 'Derek Cerda', 'school': 'Kansas', 'round': 17},
            {'name': 'Derrick Smith', 'school': 'NC State', 'round': 17},
            {'name': 'Xavier Cardenas', 'school': 'San Diego State', 'round': 17},
            {'name': 'Jared Davis', 'school': 'Virginia Tech', 'round': 17},
            {'name': 'Brody Donay', 'school': 'Florida', 'round': 17},
            {'name': 'Patrick Galle', 'school': 'Ole Miss', 'round': 17},
            {'name': 'JP Smith', 'school': 'Sacramento State', 'round': 17},
            {'name': 'Cameron Nickens', 'school': 'Austin Peay', 'round': 17},
            {'name': 'Logan Poteet', 'school': 'UNC Charlotte', 'round': 17},
            {'name': 'Anthony Karoly', 'school': 'Nova Southeastern', 'round': 17},
            {'name': 'Joel Sarver', 'school': 'UNC Charlotte', 'round': 17},
            {'name': 'Braeden Sloan', 'school': 'TCU', 'round': 17},
            {'name': 'Grayson Saunier', 'school': 'Texas', 'round': 17},
            {'name': 'Brody Fowler', 'school': 'North Greenville', 'round': 17},
            {'name': 'Luke Nowak', 'school': 'Illinois Chicago', 'round': 17},
            {'name': 'Tyler Schmitt', 'school': 'Illinois', 'round': 17},
            {'name': 'Richie Cortese', 'school': 'Lander', 'round': 17},
            {'name': 'Cannon Peebles', 'school': 'Tennessee', 'round': 17},
            {'name': 'Sam Robertson', 'school': 'Northwest Shoals', 'round': 17},
            {'name': 'Ryan Osinski', 'school': 'Virginia', 'round': 17},
            {'name': 'Sam Horn', 'school': 'Missouri', 'round': 17},
            
            # Round 18
            {'name': 'Landen Payne', 'school': 'Southern Mississippi', 'round': 18},
            {'name': 'Tyrelle Chadwick', 'school': 'Illinois State', 'round': 18},
            {'name': 'Hayden Cuthbertson', 'school': 'Miami (OH)', 'round': 18},
            {'name': 'Angelo Smith', 'school': 'Central Florida', 'round': 18},
            {'name': 'Jay Dill', 'school': 'Troy', 'round': 18},
            {'name': 'Owen Puk', 'school': 'Florida International', 'round': 18},
            {'name': 'Will Cresswell', 'school': 'Washington State', 'round': 18},
            {'name': 'Canon Reeder', 'school': 'Oregon State', 'round': 18},
            {'name': 'Julius Sanchez', 'school': 'Illinois', 'round': 18},
            {'name': 'Cooper McGrath', 'school': 'Northeastern', 'round': 18},
            {'name': 'Brayden Jones', 'school': 'Ole Miss', 'round': 18},
            {'name': 'Cade Fisher', 'school': 'Auburn', 'round': 18},
            {'name': 'Matthew Dalquist', 'school': 'UC San Diego', 'round': 18},
            {'name': 'Dylan Driessen', 'school': 'South Dakota State', 'round': 18},
            {'name': 'Connor Knox', 'school': 'George Mason', 'round': 18},
            {'name': 'Raul Garayzar', 'school': 'Arizona', 'round': 18},
            {'name': 'Aiven Cabral', 'school': 'Northeastern', 'round': 18},
            {'name': 'Matthew Potok', 'school': 'Coastal Carolina', 'round': 18},
            {'name': 'Zane Petty', 'school': 'Texas Tech', 'round': 18},
            {'name': 'Justin West', 'school': 'Louisville', 'round': 18},
            
            # Round 19
            {'name': 'Nicholas Weyrich', 'school': 'Marshall', 'round': 19},
            {'name': 'Easton Marks', 'school': 'Florida International', 'round': 19},
            {'name': 'Peyton Fosher', 'school': 'Nevada', 'round': 19},
            {'name': 'Itsuki Takemoto', 'school': 'Hawaii', 'round': 19},
            {'name': 'Luke Kovach', 'school': 'Cal Poly', 'round': 19},
            {'name': 'Brandon Cain', 'school': 'Oklahoma', 'round': 19},
            {'name': 'Blake Morgan', 'school': 'Old Dominion', 'round': 19},
            {'name': 'Matthew Becker', 'school': 'South Carolina', 'round': 19},
            {'name': 'Liam Best', 'school': 'Appalachian State', 'round': 19},
            {'name': 'Ryan Heppner', 'school': 'British Columbia', 'round': 19},
            {'name': 'Jonathan Vastine', 'school': 'Vanderbilt', 'round': 19},
            {'name': 'Robert Phelps', 'school': 'Reinhardt', 'round': 19},
            {'name': 'Joe Scarborough', 'school': 'Jacksonville State', 'round': 19},
            {'name': 'Anson Aroz', 'school': 'Oregon', 'round': 19},
            
            # Round 20
            {'name': 'Andrew Sentlinger', 'school': 'Virginia Tech', 'round': 20},
            {'name': 'Ethan Cole', 'school': 'Augustana', 'round': 20},
            {'name': 'Cannon Pickell', 'school': 'Western Carolina', 'round': 20},
            {'name': 'Sam Tookoian', 'school': 'Ole Miss', 'round': 20},
            {'name': 'Kade Brown', 'school': 'Sacramento State', 'round': 20},
            {'name': 'Juan Cruz', 'school': 'Alabama State', 'round': 20},
            {'name': 'Michael Hilker', 'school': 'Arizona', 'round': 20},
            {'name': 'Chase Heath', 'school': 'Central Missouri', 'round': 20},
            {'name': 'Freddy Rodriguez', 'school': 'Hawaii', 'round': 20},
            {'name': 'Estevan Moreno', 'school': 'Notre Dame', 'round': 20},
            {'name': 'Curtis Hebert', 'school': 'Portland', 'round': 20},
            {'name': 'Hayden Friese', 'school': 'Western Carolina', 'round': 20},
            {'name': 'Kameron Douglas', 'school': 'Alabama State', 'round': 20},
            {'name': 'Luke Cantwell', 'school': 'Pittsburgh', 'round': 20},
            {'name': 'Garrett Stratton', 'school': 'Rice', 'round': 20},
            {'name': 'Bryce Martin-Grudzielanek', 'school': 'USC', 'round': 20},
        ]
        
        # Add draft year to all 2025 picks
        for player in drafted_2025:
            player['draft_year'] = 2025
        
        # Previous years draft picks (2022-2024)
        drafted_previous = [
            # 2024 Draft - Major college players
            {'name': 'Travis Bazzana', 'school': 'Oregon State', 'draft_year': 2024, 'round': 1},
            {'name': 'Charlie Condon', 'school': 'Georgia', 'draft_year': 2024, 'round': 1},
            {'name': 'Nick Kurtz', 'school': 'Wake Forest', 'draft_year': 2024, 'round': 1},
            {'name': 'Chase Burns', 'school': 'Wake Forest', 'draft_year': 2024, 'round': 1},
            {'name': 'Braden Montgomery', 'school': 'Texas A&M', 'draft_year': 2024, 'round': 1},
            {'name': 'Jac Caglianone', 'school': 'Florida', 'draft_year': 2024, 'round': 1},
            {'name': 'Hagen Smith', 'school': 'Arkansas', 'draft_year': 2024, 'round': 1},
            {'name': 'Konnor Griffin', 'school': 'Alabama', 'draft_year': 2024, 'round': 1},
            {'name': 'Vance Honeycutt', 'school': 'North Carolina', 'draft_year': 2024, 'round': 1},
            {'name': 'JuJu Bower', 'school': 'LSU', 'draft_year': 2024, 'round': 1},
            {'name': 'Tommy Troy', 'school': 'Stanford', 'draft_year': 2024, 'round': 1},
            {'name': 'Seaver King', 'school': 'Wake Forest', 'draft_year': 2024, 'round': 2},
            {'name': 'Carson Whisenhunt', 'school': 'East Carolina', 'draft_year': 2024, 'round': 2},
            {'name': 'Ryan Waldschmidt', 'school': 'Kentucky', 'draft_year': 2024, 'round': 2},
            {'name': 'Thatcher Hurd', 'school': 'UCLA', 'draft_year': 2024, 'round': 2},
            {'name': 'Justin Crawford', 'school': 'LSU', 'draft_year': 2024, 'round': 1},
            {'name': 'Christian Moore', 'school': 'Tennessee', 'draft_year': 2024, 'round': 1},
            {'name': 'Andrew Dutkanych', 'school': 'Virginia Tech', 'draft_year': 2024, 'round': 2},
            {'name': 'Trey Yesavage', 'school': 'East Carolina', 'draft_year': 2024, 'round': 1},
            {'name': 'Ben Kudrna', 'school': 'Kansas State', 'draft_year': 2024, 'round': 2},
            
            # 2023 Draft - Major college players
            {'name': 'Dylan Crews', 'school': 'LSU', 'draft_year': 2023, 'round': 1},
            {'name': 'Wyatt Langford', 'school': 'Florida', 'draft_year': 2023, 'round': 1},
            {'name': 'Paul Skenes', 'school': 'LSU', 'draft_year': 2023, 'round': 1},
            {'name': 'Rhett Lowder', 'school': 'Wake Forest', 'draft_year': 2023, 'round': 1},
            {'name': 'Hurston Waldrep', 'school': 'Florida', 'draft_year': 2023, 'round': 1},
            {'name': 'Chase Dollander', 'school': 'Tennessee', 'draft_year': 2023, 'round': 1},
            {'name': 'Jacob Gonzalez', 'school': 'Ole Miss', 'draft_year': 2023, 'round': 1},
            {'name': 'Brayden Taylor', 'school': 'TCU', 'draft_year': 2023, 'round': 1},
            {'name': 'Cade Horton', 'school': 'Oklahoma', 'draft_year': 2023, 'round': 1},
            {'name': 'Ty Floyd', 'school': 'LSU', 'draft_year': 2023, 'round': 2},
            {'name': 'Parker Messick', 'school': 'Florida State', 'draft_year': 2023, 'round': 2},
            {'name': 'Drew Beam', 'school': 'Tennessee', 'draft_year': 2023, 'round': 2},
            {'name': 'Blade Tidwell', 'school': 'Tennessee', 'draft_year': 2023, 'round': 2},
            {'name': 'Blake Burkhalter', 'school': 'Auburn', 'draft_year': 2023, 'round': 2},
            {'name': 'Teddy McGraw', 'school': 'Florida State', 'draft_year': 2023, 'round': 2},
            
            # 2022 Draft - Major college players  
            {'name': 'Jacob Berry', 'school': 'LSU', 'draft_year': 2022, 'round': 1},
            {'name': 'Gavin Cross', 'school': 'Virginia Tech', 'draft_year': 2022, 'round': 1},
            {'name': 'Kevin Parada', 'school': 'Georgia Tech', 'draft_year': 2022, 'round': 1},
            {'name': 'Jace Jung', 'school': 'Texas Tech', 'draft_year': 2022, 'round': 1},
            {'name': 'Daniel Susac', 'school': 'Arizona', 'draft_year': 2022, 'round': 1},
            {'name': 'Cooper Hjerpe', 'school': 'Oregon State', 'draft_year': 2022, 'round': 1},
            {'name': 'Spencer Jones', 'school': 'Vanderbilt', 'draft_year': 2022, 'round': 1},
            {'name': 'Drew Gilbert', 'school': 'Tennessee', 'draft_year': 2022, 'round': 1},
            {'name': 'Landon Sims', 'school': 'Mississippi State', 'draft_year': 2022, 'round': 1},
            {'name': 'Justin Campbell', 'school': 'Oklahoma State', 'draft_year': 2022, 'round': 1},
            {'name': 'Peyton Pallette', 'school': 'Arkansas', 'draft_year': 2022, 'round': 2},
            {'name': 'Jonathan Cannon', 'school': 'Georgia', 'draft_year': 2022, 'round': 2},
            {'name': 'Cayden Wallace', 'school': 'Arkansas', 'draft_year': 2022, 'round': 2},
            {'name': 'Jake Bennett', 'school': 'Oklahoma', 'draft_year': 2022, 'round': 2},
            {'name': 'Tanner Hall', 'school': 'Oregon', 'draft_year': 2022, 'round': 2},
            {'name': 'Nolan McLean', 'school': 'Oklahoma State', 'draft_year': 2022, 'round': 2},
            {'name': 'Dylan Lesko', 'school': 'Vanderbilt', 'draft_year': 2022, 'round': 2},
            {'name': 'Brock Wilken', 'school': 'Wake Forest', 'draft_year': 2022, 'round': 2},
        ]
        
        # Combine all draft data
        all_drafted = drafted_2025 + drafted_previous
        
        self.drafted_players = pd.DataFrame(all_drafted)
        self.drafted_players['name_lower'] = self.drafted_players['name'].str.lower()
        self.drafted_players['school_name'] = self.drafted_players['school']
        
        print(f"Loaded {len(self.drafted_players)} drafted college players (2022-2025)")
    
    def filter_drafted_players(self, df: pd.DataFrame, name_col: str = 'name', 
                               team_col: str = 'team') -> pd.DataFrame:
        """
        Remove drafted players from a DataFrame.
        
        Args:
            df: DataFrame containing player data
            name_col: Column name containing player names
            team_col: Column name containing team names
            
        Returns:
            DataFrame with drafted players removed and 'is_drafted' column updated
        """
        if self.drafted_players.empty:
            self.fetch_draft_data()
        
        df = df.copy()
        
        # Create lowercase name for matching
        df['name_lower'] = df[name_col].str.lower().str.strip()
        
        # Create a set of drafted player names (just names for simpler matching)
        drafted_names = set(self.drafted_players['name_lower'].tolist())
        
        # Also create partial name matches (first and last name)
        drafted_last_names = set()
        for name in self.drafted_players['name_lower']:
            parts = name.split()
            if len(parts) >= 2:
                # Add "FirstName LastName" pattern
                drafted_last_names.add(f"{parts[0]} {parts[-1]}")
        
        # Check if player is drafted
        def check_drafted(row):
            player_name = row['name_lower']
            
            # Exact match
            if player_name in drafted_names:
                return True
            
            # Partial match (handle middle names, etc.)
            parts = player_name.split()
            if len(parts) >= 2:
                short_name = f"{parts[0]} {parts[-1]}"
                if short_name in drafted_last_names:
                    return True
            
            return False
        
        df['is_drafted'] = df.apply(check_drafted, axis=1)
        
        # Drop the temporary column
        df = df.drop(columns=['name_lower'])
        
        # Filter out drafted players
        undrafted_df = df[~df['is_drafted']].copy()
        
        drafted_count = df['is_drafted'].sum()
        print(f"Filtered out {drafted_count} drafted players, {len(undrafted_df)} remaining")
        
        # Show which players were filtered
        if drafted_count > 0:
            drafted_players = df[df['is_drafted']][name_col].tolist()
            print(f"  Drafted players found: {drafted_players[:10]}...")
        
        return undrafted_df
    
    def get_draft_summary(self) -> dict:
        """Get summary statistics about drafted players."""
        if self.drafted_players.empty:
            self.fetch_draft_data()
        
        summary = {
            'total_drafted': len(self.drafted_players),
            'by_year': self.drafted_players.groupby('draft_year').size().to_dict() if not self.drafted_players.empty else {},
            'years_covered': sorted(self.drafted_players['draft_year'].unique().tolist()) if not self.drafted_players.empty else []
        }
        
        return summary


def filter_all_data(pitching_df: pd.DataFrame, batting_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convenience function to filter both pitching and batting data.
    
    Args:
        pitching_df: DataFrame with pitching stats
        batting_df: DataFrame with batting stats
        
    Returns:
        Tuple of filtered (pitching_df, batting_df)
    """
    draft_filter = DraftFilter()
    draft_filter.fetch_draft_data()
    
    print("\nFiltering pitching data...")
    filtered_pitching = draft_filter.filter_drafted_players(pitching_df)
    
    print("\nFiltering batting data...")
    filtered_batting = draft_filter.filter_drafted_players(batting_df)
    
    return filtered_pitching, filtered_batting


def main():
    """Test draft filtering."""
    from src.data_collection import DataCollector
    
    # Collect data
    collector = DataCollector()
    pitching, batting = collector.collect_all_data(use_cache=True)
    
    # Filter to Power 4
    pitching = collector.filter_power_4(pitching)
    batting = collector.filter_power_4(batting)
    
    print(f"Before filter: {len(pitching)} pitchers, {len(batting)} batters")
    
    # Filter drafted players
    filtered_pitching, filtered_batting = filter_all_data(pitching, batting)
    
    print(f"\nAfter filter: {len(filtered_pitching)} pitchers, {len(filtered_batting)} batters")
    print(f"Removed: {len(pitching) - len(filtered_pitching)} pitchers, {len(batting) - len(filtered_batting)} batters")


if __name__ == "__main__":
    main()
