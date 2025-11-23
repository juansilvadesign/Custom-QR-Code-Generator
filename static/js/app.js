const { useState } = React;

const App = () => {
  const [content, setContent] = useState('');
  const [backgroundColor, setBackgroundColor] = useState('#FFFFFF');
  const [foregroundColor, setForegroundColor] = useState('#000000');
  const [errorLevel, setErrorLevel] = useState('M');
  const [svg, setSvg] = useState('');
  const [loading, setLoading] = useState(false);

  const generateQR = async () => {
    if (!content) return;
    setLoading(true);
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, backgroundColor, foregroundColor, errorLevel })
      });
      const data = await response.json();
      if (data.error) {
        alert('Error generating QR code: ' + data.error);
        setSvg('');
      } else {
        setSvg(data.svg || '');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Network error occurred');
    }
    setLoading(false);
  };

  const downloadSVG = () => {
    if (!svg) return;
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'qrcode.svg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return React.createElement('div', { className: 'min-h-screen bg-gray-100 p-8' },
    React.createElement('div', { className: 'max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8' },
      React.createElement('h1', { className: 'text-3xl font-bold mb-8' }, 'Custom QR Code Generator'),
      React.createElement('div', { className: 'space-y-6' },
        React.createElement('div', null,
          React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Content'),
          React.createElement('input', {
            type: 'text',
            value: content,
            onChange: (e) => setContent(e.target.value),
            placeholder: 'Enter text, URL, email, etc.',
            className: 'w-full px-4 py-2 border rounded-lg'
          })
        ),
        React.createElement('div', { className: 'grid grid-cols-2 gap-4' },
          React.createElement('div', null,
            React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Background Color'),
            React.createElement('input', {
              type: 'color',
              value: backgroundColor,
              onChange: (e) => setBackgroundColor(e.target.value),
              className: 'w-full h-10 rounded-lg cursor-pointer'
            })
          ),
          React.createElement('div', null,
            React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Foreground Color'),
            React.createElement('input', {
              type: 'color',
              value: foregroundColor,
              onChange: (e) => setForegroundColor(e.target.value),
              className: 'w-full h-10 rounded-lg cursor-pointer'
            })
          )
        ),
        React.createElement('div', null,
          React.createElement('label', { className: 'block text-sm font-medium mb-2' }, 'Error Correction'),
          React.createElement('select', {
            value: errorLevel,
            onChange: (e) => setErrorLevel(e.target.value),
            className: 'w-full px-4 py-2 border rounded-lg'
          },
            React.createElement('option', { value: 'L' }, 'Low (7%)'),
            React.createElement('option', { value: 'M' }, 'Medium (15%)'),
            React.createElement('option', { value: 'Q' }, 'Quartile (25%)'),
            React.createElement('option', { value: 'H' }, 'High (30%)')
          )
        ),
        React.createElement('button', {
          onClick: generateQR,
          disabled: loading,
          className: 'w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50'
        }, loading ? 'Generating...' : 'Generate QR Code'),
        svg && React.createElement('div', { className: 'mt-8 flex flex-col items-center space-y-4' },
          React.createElement('div', {
            dangerouslySetInnerHTML: { __html: svg },
            className: 'border-2 border-gray-200 p-4 rounded-lg w-full max-w-md'
          }),
          React.createElement('button', {
            onClick: downloadSVG,
            className: 'bg-green-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-green-700'
          }, 'Download SVG')
        )
      )
    )
  );
};

ReactDOM.render(React.createElement(App), document.getElementById('root'));
