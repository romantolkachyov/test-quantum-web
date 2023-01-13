import './Button.css'

function Button({ onClick, state, ...props }) {
  return (
    <button onClick={onClick} { ... state === 'active' ? {} : {disabled: "disabled"} } className="Button" {... props}>
      {state === 'active' ? "Start" : state}
    </button>
  )
}
export default Button
