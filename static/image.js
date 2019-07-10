import React from 'react';
import ReactDOM from 'react-dom';
class image extends React.Component{
  render(){
    var value = {{book[1]}};
    return(
      <img src="http://covers.openlibrary.org/b/isbn/" + {value} + "-L.jpg" />
    );
  }
};
ReactDOM.render(
  <image />,
    document.getElementById('imageBox')
  );
