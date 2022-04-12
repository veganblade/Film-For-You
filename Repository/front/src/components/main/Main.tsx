import './Main.scss';
import {useDispatch} from "react-redux";
import {Link} from "react-router-dom";
import {signOut} from "../../redux/actionCreators";
import {FormEvent, useState} from "react";
// @ts-ignore
import ReactStars from "react-rating-stars-component";
// @ts-ignore
import TagsInput from 'react-tagsinput';
import 'react-tagsinput/react-tagsinput.css';

export default function Main() {
  const dispatch = useDispatch();
  const [ movieContent, setMovieContent ] = useState<any>(null);
  const [ searchInput, setSearchInput ] = useState('');
  const [ genre, setGenre ] = useState('');
  const [ tags, setTags ] = useState([]);
  const [ tag, setTag ] = useState('');
  const [ year, setYear ] = useState('');
  const isAdmin = localStorage.getItem('isAdmin');

  async function onRatingChange(newRating: string, movieId: string) {
    const username = localStorage.getItem('login');
    return await fetch(`http://localhost:8080/movie/addScore?username=${username}&movieId=${movieId}&score=${newRating}`);
  }

  async function starMovie(currentState: boolean, movieId: string) {
    const username = localStorage.getItem('login');
    return await fetch(`http://localhost:8080/fav/addMovie?username=${username}&movieId=${movieId}&label=${currentState ? '0' : '1'}`)
      .then((response: any) => response.json());
  }

  async function searchMovies() {
    const username = localStorage.getItem('login');
    const movies: string[] = await fetch(`http://localhost:8080/movie/getFiltred?title=${searchInput || ''}&tags=${tags.length ? tags : ''}&year=${year || ''}&genres=${genre || ''}&offset=0&limit=20`)
      .then((response: any) => response.json());
    const staredMovies: any[] = await fetch(`http://localhost:8080/user/getFavs?username=${username}`)
      .then((response: any) => response.json());

    if (movies.length === 0) {
      return setMovieContent('По вашему запросу ничего не найдено!');
    }

    setMovieContent(movies.reduce((acc: any, curr: any) => {
      const isMovieStared: boolean = staredMovies.includes(Number(curr.movieId));
      acc.push(<div className={'movie'}>
        <div className={'movie-buttons'}>
          <button onClick={() => starMovie(isMovieStared, curr.movieId)}
                  className={`movie-star ${isMovieStared ? 'movie-stared' : '' }`}>В избранное</button>
          <ReactStars
            count={5}
            value={curr.score ? curr.score : null}
            onChange={(newRating: any) => onRatingChange(newRating, curr.movieId)}
            size={24}
            isHalf={true}
            emptyIcon={<i className="far fa-star"></i>}
            halfIcon={<i className="fa fa-star-half-alt"></i>}
            fullIcon={<i className="fa fa-star"></i>}
            activeColor="#ffd700"
          />
        </div>
        <span className={'movie-field movie-title'}>{curr.title}</span>
        <span className={'movie-field movie-year'}>Год выпуска: {curr.year}</span>
        <span className={'movie-field movie-tags'}>Жанры: {curr.genres}</span>
        <span className={'movie-field movie-tags'}>Теги: {curr.tags ? curr.tags : '—'}</span>
      </div>);
      return acc;
    }, []));
  }

  function onSelectChange(e: any) {
    setGenre(e.target.value);
  }

  return (
    <>
      <header className={'main-header'}>
        <Link to={'/profile'}>
          <span className={'main-profilePage'}>Страница пользователя</span>
        </Link>
        <span className={'main-logo'}> Film For U </span>
        <div className={'main-helpersButtons'}>
          {isAdmin &&
          <Link to={'/admin'}>
            <span className={'main-adminPage'}>Панель админа</span>
          </Link>
          }
          <span className={'main-signout'} onClick={() => {
            dispatch(signOut());
            localStorage.removeItem('login');
            localStorage.removeItem('password');
          }}>Выйти</span>
        </div>
      </header>
      <main className={'main'}>
        <section className={'main-filters'}>
          <div className={'main-sendFilters'}>
            <input className={'main-search'}
                   value={searchInput}
                   onChange={(e: any) => setSearchInput(e.target.value)}/>
            <button className={'main-searchButton'} onClick={searchMovies}>Поиск</button>
          </div>
          <span className={'main-filterName'}>Жанр</span>
          <select onChange={onSelectChange} name={'genre'} className={'main-selectFilter'}>
            <option value={''}>Выберите жанр</option>
            <option value={'Horror'}>Horror</option>
            <option value={'Adventure'}>Adventure</option>
            <option value={'Children'}>Children</option>
            <option value={'Documentary'}>Documentary</option>
            <option value={'Comedy'}>Comedy</option>
            <option value={'IMAX'}>IMAX</option>
            <option value={'Action'}>Action</option>
            <option value={'Western'}>Western</option>
            <option value={'Musical'}>Musical</option>
            <option value={'Romance'}>Romance</option>
            <option value={'War'}>War</option>
            <option value={'Fantasy'}>Fantasy</option>
            <option value={'Animation'}>Animation</option>
            <option value={'Mystery'}>Mystery</option>
            <option value={'Drama'}>Drama</option>
            <option value={'Crime'}>Crime</option>
            <option value={'Film-Noir'}>Film-Noir</option>
            <option value={'Sci-Fi'}>Sci-Fi</option>
            <option value={'Thriller'}>Thriller</option>
          </select>
          <span className={'main-filterName'}>Год выпуска</span>
          <input className={'main-yearSearch'} type={'number'} onChange={(e: any) => setYear(e.target.value)}/>
          <span className={'main-filterName'}>Теги:</span>
          <TagsInput value={tags} onChange={(tags: any) => setTags(tags)}
                     inputValue={tag}
                     onChangeInput={(tag: any) => setTag(tag)}
                     focusedClassName={'tagsInput--focused'}
                     tagProps={{
                       className: 'react-tagsinput-tag tagsInput-blueColored',
                       classNameRemove: 'react-tagsinput-remove'
                     }}
                     inputProps={{
                       className: 'react-tagsinput-input',
                       placeholder: 'Добавьте теги'
                     }}/>
        </section>
        <section className={'main-movies'}>
          <div>{movieContent ? movieContent : 'Введите фильтры'}</div>
        </section>
      </main>
    </>
  )
}