from os import path, terminal_size
import sqlite3
from sqlite3.dbapi2 import Error, Timestamp, enable_shared_cache
from flask.testing import FlaskClient
import pandas as pd
import time
import json
import sql_tools
from sql_tools import query_exec, regular_LIKE_str_query
import parse_tools
from parse_tools import query_constraint_title_normalize, genresNormalize, usernameConstr, query_contraint_if_not_null_to_list, tagConstr
import uuid

GENRES_REG = None
with open("bd/genresReg.txt", "r") as reg: #реестр имеющихся жанров
    GENRES_REG = set(reg.read().split(','))
 

#ФИЛЬМЫ
def add_movie(title: str, genres: list, year: int): #доступно только администрацию
    genres = genresNormalize(genres)
    setGenres = set(genres)
    try:
        query_exec(
            f"""
            INSERT INTO movies(title,genres,year) VALUES ('{title}','{(',').join(setGenres).title()}',{year});
            """
        )
    except Error as err:
        return False 
    reg = open("bd/genresReg.txt", "a") #добавляем уникальные жанры
    for i in setGenres:
        if i not in GENRES_REG:
            GENRES_REG.add(i)
            reg.write(',' + i)
    reg.close()
    return True
def delete_movie(movieId: int):
    try:
        query_exec(
            f"""
            DELETE FROM movies WHERE movieId = {movieId};
            """
        )
        return True
    except:
        return False
#РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
def registration_user(username: str, password: str): #плохойкод
    if not usernameConstr(username):
        return json.dumps({
            'message' : 'BadUsername'
        }) 
    try:
        query_exec(
            f"""
            INSERT INTO users(username, password) VALUES ('{username}','{password}');
            """
        )
        return json.dumps({
            'message' : 'no no no'
        }) 
    except:
        return json.dumps({
            'message' : 'No bro try again'
        })      
def delete_user(username: int):
    try:
        query_exec(
            f"""
            DELETE FROM users WHERE username = '{username}';
            """
        )
        return True
    except:
        return False
def authorize_user(username: str, password: str) -> bool:
    try:
        res = query_exec(
            f"""
            SELECT * FROM users WHERE username = '{username}' AND password = '{password}'
            """
        )
        return len(res) != 0
    except:
        return False
#ОЦЕНКИ ФИЛЬМАМ
def add_score(userId:  int, movieId: int, score):
    try:
        try:
            score = int(score)
            if score < 1 or score > 5: score = 1
            timestamp = int(time.time()) 
            query_exec(
                f"""
                INSERT INTO ratings(userId,movieId,rating, timestamp) VALUES ({userId},{movieId},{score},{timestamp}) 
                ON CONFLICT(userId,movieId) 
                DO UPDATE SET rating = {score}, timestamp = {timestamp};
                """
            )
            return True
        except ValueError:
            query_exec(
                f"""
                DELETE FROM ratings WHERE userId = {userId} AND movieId = {movieId};
                """
            )
            return True
    except:
        return False
#@app.route('/movie/getScore')
def get_movie_avgScore(movieId: int) -> float:
    try:
        res = query_exec(
            f"""
            SELECT avg_score FROM movies_ratings WHERE movieId = {movieId}
            """
        )
        return res[0][0]
    except:
        return False
def get_user_score(movieId:int, userId:int) -> int:
    try:
        res = query_exec(
            f"""
            SELECT rating FROM ratings WHERE userId = {userId} AND movieId = {movieId}
            """
        )
        return res[0][0]
    except Error as err:
        return False
def get_user_scored(userId: int) -> json:
    try:
        res = query_exec(
            f"""
            SELECT movieId FROM ratings WHERE userId = {userId} 
            """
        )
        res = [i[0] for i in res]
        return get_full_info_movies_by_id(res,userId)
    except Error as err:
        return False
#ТЕГИ:
def add_tag(userId:  int, movieId: int, tag: str): #на скорую руку
    try:
        if not tagConstr(tag):
            return json.dumps({
                'message' : 'BadTag'
            }) 
        tag = tag.lower().strip()

        timestamp = int(time.time())
        query_exec(
            f"""
            INSERT INTO tags(userId,movieId,tag,timestamp) VALUES ({userId},{movieId},'{tag}',{timestamp});
            """
        )
        return json.dumps({
            'message' : 'no no no'
        }) 
    except:
        return json.dumps({
            'message' : 'No bro try again'
        }) 
def delete_tag(userId: int, movieId: int, tag: str):
    try:
        tag = tag.lower().strip()
        query_exec(
            f"""
            DELETE FROM tags WHERE userId = {userId} AND movieId = {movieId} AND tag = '{tag}';
            """
        )
        return True
    except Error as err:
        return False
def get_all_user_film_tags(userId: int, movieId: int, limit: int = 10): #возвращает список всех тегов выставленных пользователем определенному фильму в виде json файла
    try:
        res = query_exec(
            f"""
            SELECT tag FROM tags WHERE userId = {userId} AND movieId = {movieId}
            LIMIT {limit}
            """
        )
        res = [i[0] for i in res]
        return res
    except Error as err:
        return False
def get_all_film_tags(movieId: int, limit: int = 10): #возвращает все теги определенного фильма отсортированных по количеству отметок
    try:
        res = query_exec(
            f"""
            SELECT tag FROM movies_tags WHERE movieId = {movieId}
            ORDER BY count DESC
            """
        )
        res = [i[0] for i in res] #, key=lambda x: x[1])]

        return res
    except Error as err:
        return False
#ПОИСК ФИЛЬМОВ
def get_filtred_films(title: str = None, year: list = None, genres: list = None, tags: list = None, offset: int = 0, limit: int = 20) -> json: # where ind > offset(0) top limit
    try:
        prs = lambda x: parse_tools.query_contraint_if_not_null_to_list(parse_tools.query_constraint_from_none_to_null(x))
        title = query_constraint_title_normalize(title, withbrackets=True)
        year = prs(year) #'NULL' если был None, иначе - массив
        genres = prs(genres) #...
        tags = prs(tags) #...
        res = query_exec(
            f"""
            SELECT movies.movieId
            FROM movies
            LEFT JOIN (SELECT movies_tags.movieId as tagmovId, COUNT(tag) as cnt_tag
                    FROM movies_tags 
                    WHERE {sql_tools.regular_IN_str_query(tags, 'tag')}
                    GROUP BY 1) tag_cnstr ON tag_cnstr.tagmovId = movies.movieId
            LEFT JOIN movies_ratings m_r ON m_r.movieId = movies.movieId
            WHERE 
                title LIKE '%' || COALESCE({title}, '') || '%' AND 
                {sql_tools.regular_IN_str_query(year, 'year')} AND
                {regular_LIKE_str_query(genres, 'genres')} AND 
                {f'tag_cnstr.cnt_tag = {len(tags)}' if tags != 'NULL' else 'TRUE'}
            GROUP BY movies.movieId
            ORDER BY m_r.avg_score DESC 
            LIMIT {limit} OFFSET {offset}
            """
        ) 
        res = [str(i[0]) for i in res]
        return get_full_info_movies_by_id(res)
    except Error as err:
        return err
#ДОБАВИТЬ В ИЗБРАННОЕ 
def add_movie_to_favorite(userId, movieId, label: str) -> bool:
    try:
        timestamp = int(time.time())
        label = bool(int(label))
        if label:
            query_exec(
                f"""
                INSERT INTO users_favorites(userId,movieId,timestamp) VALUES ({userId}, {movieId}, {timestamp})
                """
            )
        else:
            query_exec(
                f"""
                DELETE FROM users_favorites WHERE userId = {userId} AND movieId = {movieId}
                """
            )
        return True
    except Error as err:
        return err
def get_user_favorites(userId):
    try:
        res = query_exec(
            f"""
            SELECT movieId FROM users_favorites WHERE userId = {userId}
            ORDER BY timestamp DESC
            """
        )
        res = [i[0] for i in res]
        return res
        #get_full_info_movies_by_id(res,userId)
    except Error as err:
        return False
#ИНФОРМАЦИЯ ОБ АККАУНТЕ
def get_username(userId) -> str:
    try: 
        username = query_exec(
            f"""
            SELECT username FROM users WHERE userId = {userId}
            """
        )
        return username[0][0]
    except Error as err:
        return False
def get_count_user_ratings(userId) -> int:
    try:
        res = query_exec(
            f"""
            SELECT COUNT(*) FROM ratings WHERE userId = {userId} 
            """
        )
        return res[0][0]
    except Error as err:
        return False
def get_count_user_favorites(userId) -> int:
    try:
        res = query_exec(
            f"""
            SELECT COUNT(*) FROM users_favorites WHERE userId = {userId} 
            """
        )
        return res[0][0]
    except Error as err:
        return False
def get_acc_info(userId):
    try:
        username = get_username(userId)
        count_rated = get_count_user_ratings(userId)
        count_favorites = get_count_user_favorites(userId)

        return json.dumps(
            {
                'username' : username,
                'count_rated' : count_rated,
                'count_favorites' : count_favorites
            }
        )
    except Error as err:
        return False
def get_user_id(username: str):
    try: 
        userId= query_exec(
            f"""
            SELECT userId FROM users WHERE username = '{username}'
            """
        )
        return userId[0][0]
    except Error as err:
        return err
#   get_user_scored(userId)
#   get_user_favorites(userId)
def get_allUsers(offset: int = 0, limit: int = 20):
    offset = int(offset)
    offset += 610
    res = query_exec(
        f"""
            SELECT userId,username,password FROM users 
            ORDER BY 1 
            LIMIT {limit} OFFSET {offset};
        """
    )
    jsres = []
    for i in res:
        jsres.append(
            {
                'userId' : i[0],
                'username' : i[1],
                'password' : i[2]
            } 
        )
    return json.dumps(jsres)
def user_sendMesg(userId, text):
    try:
        path = f'messages/{str(userId)}_{str(uuid.uuid1())}.txt'
        f = open(path, 'w')
        f.write(text)
        f.close()

        return True
    except:
        return False
#ВЫВОД ИНФОРМАЦИИ
def get_columInfo_by_movieid(movieId: list, table:str, column: str, addCond: str = 'TRUE'): #только 1 столбец
    if type(movieId) != list:
        movieId = [movieId]
    res = query_exec(
        f"""
        SELECT {column} FROM {table} WHERE {sql_tools.regular_IN_str_query(movieId, 'movieId')} AND {addCond}
        """
    )
    return [i[0] for i in res]
def get_full_info_movies_by_id(movieId: list, userId: int = None): #самая худшая функция 
    if type(movieId) == str:
        movieId = query_contraint_if_not_null_to_list(movieId)
    if type(movieId) != list:
        movieId = [movieId]
    f = lambda x: get_columInfo_by_movieid(movieId,'movies', x)
    titles = f('title')
    genres = f('genres')
    years = f('year')
    score = None
    if not userId:
        score = get_columInfo_by_movieid(movieId, 'movies_ratings', 'avg_score')
        tags = [','.join(get_all_film_tags(i)) for i in movieId]
    else:
        scc = get_columInfo_by_movieid(movieId, 'ratings', 'rating', f'userId = {userId}')
        tags = [','.join(get_all_user_film_tags(userId, i)) for i in movieId]

    res = []
    for i in range(len(movieId)):
        if score:
            try:
                sc = score[i]
            except:
                sc = 0
        else: 
            try:
                sc = scc[i]
            except:
                sc = 0
        res.append(
            {
                'movieId' : movieId[i],
                'title' : titles[i],
                'genres' : genres[i],
                'year' : years[i],
                'score' : sc,
                'tags' : tags[i]
            }
        )
    return json.dumps(res)