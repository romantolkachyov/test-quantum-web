import './Button.css'

function Button({ onClick }) {
  return (
    <button onClick={onClick} className="Button">
      Start
    </button>
  )
}
export default Button
