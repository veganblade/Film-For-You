import {FC, useCallback, useEffect, useState} from "react";
import "./Admin.scss";
import {generateUniqueId} from "../../helpers";

interface AdminProps {

}

const Admin: FC<AdminProps> = () => {
  const [uniqueId, setUniqueId] = useState(generateUniqueId());
  const [users, setUsers] = useState([]);
  const [movieToDelete, setMovieToDelete] = useState('');
  const [userToPromote, setUserToPromote] = useState('');
  const [movieName, setMovieName] = useState('');
  const [moviesContent, setMoviesContent] = useState<any>(null);
  const [year, setYear] = useState('');
  const [genre, setGenre] = useState('');

  setInterval(() => {
    setUniqueId(generateUniqueId());
  }, 500);

  const addMovie = useCallback(async () => {
    return await fetch(`http://localhost:8080/movie/add?title=${movieName}&genres=${genre}&year=${year}`)
      .then((response: any) => response.json());
  }, [movieName, genre, year]);

  async function deleteUser(username: string) {
    return await fetch(`http://localhost:8080/admin/deleteUser?username=${username}`);
  }

  async function deleteMovieById(movieId: string | number) {
    return await fetch(`http://localhost:8080/admin/deleteMov?movieId=${movieId || movieToDelete}`);
  }

  async function promoteUserByUserName() {
    return await fetch(`http://localhost:8080/admin/giveAdminRoot?username=${userToPromote}`);
  }

  async function searchMovies() {
    const movies = await fetch(`http://localhost:8080/movie/getFiltred?title=${movieName}&year=&genres=&tags=&offset=${0}&limit=${5}`)
      .then((response: any) => response.json());

    if (movies.length === 0) {
      return setMoviesContent('Ни одного фильма не найдено!');
    }

    setMoviesContent(movies.reduce((acc: any, curr: any) => {
      // @ts-ignore
      acc.push(<div className={'movie'} id={curr.movieId}>
        <span className={'movie-field movie-title'}>{curr.title}</span>
        <span className={'movie-field movie-genres'}>Жанры: {curr.genres}</span>
        <span className={'movie-field movie-genres'}>ID: {curr.movieId}</span>
        <button className={'admin-userRemove'} onClick={() => {
          document.getElementById(curr.movieId)!.remove();
          deleteMovieById(curr.movieId);
        }}>X</button>
      </div>);
      return acc;
    }, []));
  }

  const getUsers = useCallback(async () => {
    const users: [] = await fetch(`http://localhost:8080/admin/getAllUsers?offset=0&limit=20`).then((response: any) => response.json());
    setUsers(users.reduce((acc: any, curr: any) => {
      acc.push(<div className={'user'} id={curr.movieId}>
        <span className={'user-id'}></span>
        <span className={'user-login'}>Логин: {curr.username}</span>
        <span className={'user-password'}>Пароль: {curr.password}</span>
        <button className={'admin-userRemove'} onClick={() => deleteUser(curr.username)}>X</button>
      </div>);
      return acc;
    }, []));
  }, []);



  useEffect(() => {
    getUsers();
  }, []);

  return (
    <main className={'admin'}>
      <h2 className={'admin-header'}>Админская панель</h2>
      <div className={'admin-movies'}>
        <h2>Управление фильмами</h2>
        <div className={'admin-addMovie'}>
          <span className={'admin-fieldName'}>Название</span>
          <input className={'admin-movieInput'} value={movieName} onChange={(e: any) => setMovieName(e.target.value)}/>
          <span className={'admin-fieldName'}>Жанр</span>
          <input className={'admin-movieInput'} value={genre} onChange={(e: any) => setGenre(e.target.value)}/>
          <span className={'admin-fieldName'}>Год выпуска</span>
          <input className={'admin-movieInput'} value={year} onChange={(e: any) => setYear(e.target.value)}/>
          <button onClick={addMovie} className={'admin-addMovieButton'}>Добавить</button>
        </div>
        <h3>Удалить фильм</h3>
        <span className={'admin-movieIdToDelete'}>ID фильма для удаления</span>
        <div className={'admin-deleteMovie'}>
          <input value={movieToDelete} onChange={(e: any) => setMovieToDelete(e.target.value)} className={'admin-movieInput'} />
          <button onClick={() => deleteMovieById('')} className={'admin-deleteMovieButton'}>Удалить</button>
        </div>
        <div className={'admin-addMovie'}>
          <h3>Искать фильм</h3>
          <input className={'admin-movieInput'} value={movieName} onChange={(e: any) => setMovieName(e.target.value)}/>
          <button onClick={searchMovies} className={'admin-addMovieButton'}>Искать</button>
        </div>
        {
          moviesContent ?
            <>
              <h2>Фильмы:</h2>
              <div>{moviesContent}</div>
            </>
            : null
        }

      </div>
      <div className={'admin-users'}>
        <h2>Управление пользователями</h2>
        <span className={'admin-promoteUser'}>Сделать пользователя админом (by username):</span>
        <div className={'admin-userPromote'}>
          <input value={userToPromote} onChange={(e: any) => setUserToPromote(e.target.value)} className={'admin-movieInput'} />
          <button onClick={promoteUserByUserName} className={'admin-promoteUserButton'}>Выдать права администратора</button>
        </div>
        <h3>Пользователи:</h3>
        {users}
      </div>
    </main>
  )
}

export default Admin;