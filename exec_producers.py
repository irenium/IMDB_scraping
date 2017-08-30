import json


def make_producer_dict():
    """
    Opens json file w/movie info and returns a dictionary 
    of information about executive producers and the movies 
    they were involved in prior to becoming an exec producer.
    """

    with open('movies_6feb2017.json','rb') as infile:
        movie_dicts = json.load(infile)    
        
    producers_dict = {}
    for movie in movie_dicts:
        for name, role in movie["full_credits"]:
            if ("executive producer" in role) and (name not in producers_dict):
                producers_dict[name.strip()] = []

    for movie in movie_dicts:
        try:
            movie["num_ratings"] = float(movie["num_ratings"].replace(',',''))
        except AttributeError:
            pass
        
        if movie["num_ratings"] > 500:            
            for name, role in movie["full_credits"]:
                if name.strip() in producers_dict:
                    for person, team in movie["credits_by_teams"]:
                        if person == name:
                            try:
                                producers_dict[name.strip()].append(tuple([role.strip(), int(movie["release_year"]),
                                        movie["production_co"], float(movie["rating"]),
                                        team.strip()]))
                            except (ValueError, TypeError):
                                producers_dict[name.strip()].append(tuple([role.strip(), None,
                                        movie["production_co"], 0, team.strip()]))

    for key, info in producers_dict.iteritems():
        info.sort(key=lambda tup: tup[1])

    return producers_dict


def get_lists(producers_dict):
    """
    Analyzes a dictionary of information on exec producers,
    and returns several lists of data regarding each exec
    producer's previous experience.
    """

    imdb_ratings, year_index, num_roles = [], [], []
    num_studios = []
    num_teams, teams, num_producer_roles = [], [], []
    num_animator_roles, num_writer_roles, num_director_roles, num_fx_roles = [], [], [], []
    
    for key, tuple_list in producers_dict.iteritems():
        for idx, (t1, t2, t3, t4, t5) in enumerate(tuple_list):
            #if t1 == "executive producer":
            if (t1 == u'executive producer' and t4 != 0):
                imdb_ratings.append(t4)
                year_index.append(t2)
                num_roles.append(len(tuple_list[:idx]))
                teams.append(tuple_list[:idx])
                break      
                
    for entry in teams:
        temp_list = []
        anima_count, writer_count, director_count, fx_count, producer_count = 0, 0, 0, 0, 0
        
        for idx, (t1, t2, t3, t4, t5) in enumerate(entry):
            temp_list.append(t5)
            if t5 == "Animation Department":
                anima_count += 1
            elif t5 == "Writing Credits":
                writer_count += 1
            elif t5 == "Directed by":
                director_count += 1
            elif t5 == "Visual Effects by":
                fx_count += 1
            elif t5 == "Produced by":
                producer_count += 1
                
        num_teams.append(len(set(temp_list)))
        num_animator_roles.append(anima_count)
        num_writer_roles.append(writer_count)
        num_director_roles.append(director_count)
        num_fx_roles.append(fx_count)
        num_producer_roles.append(producer_count)
        
    return (imdb_ratings, num_roles, num_animator_roles, 
            num_writer_roles, num_director_roles, 
            num_teams, num_fx_roles, num_producer_roles)