const InputField = ({ type, value, onChange, placeholder }) => (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="input-field"
      required
    />
  );
  
  export default InputField;
  