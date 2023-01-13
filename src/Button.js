import './Button.css'

function Button({ onClick, state }) {
  if (state === 'active') {
    return (
      <button onClick={onClick} className="Button">
        Start
      </button>
    )
  } else {
    return (
      <button disabled="disabled" className="Button">
        {state}
      </button>
    )
  }
}
export default Button
