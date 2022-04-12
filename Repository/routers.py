import json
from re import M
from flask.ctx import after_this_request
import SoftDaC_Project as back
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app
)
OK = json.dumps({
    'message' : 'no no no'
})
ERR = json.dumps({
    'message' : 'No bro try again'
})

ADMINS = ['superadmin']

def doF(bol):
    if bol: return OK
    return ERR
def userId(username):
    return back.get_user_id(username)

@app.route('/movie/add')
def addMovie():
    r = request.args
    return doF(back.add_movie(
        r['title'],
        r['genres'],
        r['year']))
@app.route('/movie/getScore')
def movieGetScore():
    r = request.args
    return str(back.get_movie_avgScore(r['movieId']))
@app.route('/movie/addScore')
def addScore():
    r = request.args
    usId = userId(r['username'])
    return doF(back.add_score(
        usId,
        r['movieId'],
        r['score']
    ))
@app.route('/movie/getUserScore')
def getUserScore():
    r = request.args
    usId = userId(r['username'])

    return str(back.get_user_score(
        r['movieId'],
        usId
    ))
@app.route('/movie/getFiltred')
def getFiltredMovies():
    r = request.args
    return back.get_filtred_films(
        r['title'],
        r['year'],
        r['genres'],
        r['tags'],
        r['offset'],
        r['limit']
    )
@app.route('/user/reg')
def regUser():
    r = request.args
    return back.registration_user( #на беке бека уже джос сообщение генерится
        r['username'],
        r['password']
    )
@app.route('/user/aut')
def autUser():
    r = request.args
    if back.authorize_user(r['username'],r['password']):
        if r['username'] in ADMINS:
            return json.dumps({
                'message' : 'success', 
                'isAdmin' : 'true'

            })
        else:
            return json.dumps({
                'message' : 'success', 
                'isAdmin' : 'false'

            })
    else:
        return ERR
@app.route('/user/getScored')
def getUserScored():
    r = request.args
    usId = userId(r['username'])
    
    return back.get_user_scored(
        usId
    )
@app.route('/user/getFavs')
def getUserFavs():
    r = request.args
    usId = userId(r['username'])

    return str(back.get_user_favorites(usId))
@app.route('/user/getFullFavs')
def getFullUserFavs():
    r = request.args
    usId = userId(r['username'])
    return back.get_full_info_movies_by_id(back.get_user_favorites(usId), usId)
@app.route('/user/sendMesg')
def userSendMesg():
    r = request.args

    return doF(back.user_sendMesg(
        r['userId'],
        r['mesg']
    ))
@app.route('/tag/add')
def addTag():
    r = request.args
    usId = userId(r['username'])

    return back.add_tag( ##на беке бека уже джсон сообщение генерится
        usId,
        r['movieId'],
        r['tag']
    )
@app.route('/tag/del')
def deleteTag():
    r = request.args
    usId = userId(r['username'])

    return doF(back.delete_tag(
        usId,
        r['movieId'],
        r['tag']
    ))
@app.route('/tag/allUserMovieT')
def allUserMovieTags():
    r = request.args
    usId = userId(r['username'])

    return back.get_all_user_film_tags(
        usId,
        r['movieId'],
        r['limit']
    )
@app.route('/tag/allMovieT')
def allMovieTag():
    r = request.args

    return back.get_all_film_tags(
        r['movieId'],
        r['limit']
    )


@app.route('/fav/addMovie')
def addMovieToFav():
    r = request.args
    
    return doF(back.add_movie_to_favorite(
        userId(r['username']),
        r['movieId'],
        r['label']
    ))

@app.route('/user/accInfo')
def getAccInfo():
    r = request.args

    return back.get_acc_info(
        userId(r['username'])
    )

@app.route('/admin/deleteMov')
def deleteMovie():
    r = request.args
    return doF(back.delete_movie(r['movieId']))
@app.route('/admin/deleteUser')
def delUser():
    r = request.args
    return doF(back.delete_user(
        r['username']
    ))
@app.route('/admin/getAllUsers')
def getAllUsers():
    r = request.args

    return back.get_allUsers(
        r['offset'],
        r['limit']
    )
@app.route('/admin/giveAdminRoot')
def giveAdminRoot():
    r = request.args
    ADMINS.append(r['username'])

    return OK
