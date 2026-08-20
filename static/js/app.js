const { useState } = React;

const App = () => {
  const [content, setContent] = useState('');
  const [background, setBackground] = useState('#FFFFFF');
  const [foreground, setForeground] = useState('#000000');
  const [errorCorrection, setErrorCorrection] = useState('M');
  const [border, setBorder] = useState(4);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateQR = async () => {
    if (!content || loading) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          payloadType: 'text',
          fields: { text: content },
          background,
          foreground,
          errorCorrection,
          border,
          outputName: 'qrcode.svg'
        })
      });
      const data = await response.json();
      if (!response.ok || data.error) {
        setResult(null);
        setError(data.error || {
          code: 'unexpected_response',
          message: 'The server returned an unexpected response.'
        });
        return;
      }
      setResult(data);
    } catch (_networkError) {
      setResult(null);
      setError({
        code: 'network_error',
        message: 'The generator could not be reached. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadSVG = () => {
    if (!result?.svg) return;
    const blob = new Blob([result.svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = result.metadata?.fileName || 'qrcode.svg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return React.createElement('main', { className: 'min-h-screen bg-gray-100 p-4 sm:p-8' },
    React.createElement('section', { className: 'max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6 sm:p-8' },
      React.createElement('h1', { className: 'text-3xl font-bold mb-2' }, 'Custom QR Code Generator'),
      React.createElement('p', { className: 'text-sm text-gray-600 mb-8' },
        'Your content is processed for this response only and is not shown in result metadata.'
      ),
      React.createElement('div', { className: 'space-y-6' },
        React.createElement('div', null,
          React.createElement('label', { htmlFor: 'content', className: 'block text-sm font-medium mb-2' }, 'Text content'),
          React.createElement('textarea', {
            id: 'content',
            rows: 4,
            value: content,
            onChange: (event) => setContent(event.target.value),
            placeholder: 'Enter exact text to encode',
            className: 'w-full px-4 py-2 border rounded-lg'
          })
        ),
        React.createElement('div', { className: 'grid grid-cols-2 gap-4' },
          React.createElement('div', null,
            React.createElement('label', { htmlFor: 'background', className: 'block text-sm font-medium mb-2' }, 'Background'),
            React.createElement('input', {
              id: 'background', type: 'color', value: background,
              onChange: (event) => setBackground(event.target.value.toUpperCase()),
              className: 'w-full h-10 rounded-lg cursor-pointer'
            })
          ),
          React.createElement('div', null,
            React.createElement('label', { htmlFor: 'foreground', className: 'block text-sm font-medium mb-2' }, 'QR modules'),
            React.createElement('input', {
              id: 'foreground', type: 'color', value: foreground,
              onChange: (event) => setForeground(event.target.value.toUpperCase()),
              className: 'w-full h-10 rounded-lg cursor-pointer'
            })
          )
        ),
        React.createElement('div', { className: 'grid grid-cols-2 gap-4' },
          React.createElement('div', null,
            React.createElement('label', { htmlFor: 'error-correction', className: 'block text-sm font-medium mb-2' }, 'Error correction'),
            React.createElement('select', {
              id: 'error-correction', value: errorCorrection,
              onChange: (event) => setErrorCorrection(event.target.value),
              className: 'w-full px-4 py-2 border rounded-lg'
            },
              React.createElement('option', { value: 'L' }, 'Low (L)'),
              React.createElement('option', { value: 'M' }, 'Medium (M)'),
              React.createElement('option', { value: 'Q' }, 'Quartile (Q)'),
              React.createElement('option', { value: 'H' }, 'High (H)')
            )
          ),
          React.createElement('div', null,
            React.createElement('label', { htmlFor: 'border', className: 'block text-sm font-medium mb-2' }, 'Quiet zone'),
            React.createElement('select', {
              id: 'border', value: border,
              onChange: (event) => setBorder(Number(event.target.value)),
              className: 'w-full px-4 py-2 border rounded-lg'
            },
              React.createElement('option', { value: 4 }, '4 modules (recommended)'),
              React.createElement('option', { value: 3 }, '3 modules (warning)'),
              React.createElement('option', { value: 2 }, '2 modules (warning)'),
              React.createElement('option', { value: 6 }, '6 modules')
            )
          )
        ),
        React.createElement('button', {
          type: 'button', onClick: generateQR, disabled: loading || !content,
          className: 'w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50'
        }, loading ? 'Generating…' : 'Generate QR Code'),
        React.createElement('div', { 'aria-live': 'polite' },
          error && React.createElement('p', { className: 'rounded bg-red-50 p-3 text-red-800' },
            `${error.message} (${error.code})`
          )
        ),
        result && React.createElement('section', { className: 'mt-8 flex flex-col items-center space-y-4' },
          React.createElement('div', {
            dangerouslySetInnerHTML: { __html: result.svg },
            className: 'border-2 border-gray-200 p-4 rounded-lg w-full max-w-md',
            'aria-label': 'Generated QR code preview'
          }),
          React.createElement('p', { className: 'text-sm text-gray-700 text-center' }, result.summary),
          result.warnings?.map((warning) =>
            React.createElement('p', {
              key: warning.code,
              className: 'w-full rounded bg-amber-50 p-3 text-sm text-amber-900'
            }, warning.message)
          ),
          React.createElement('dl', { className: 'grid grid-cols-2 gap-x-6 gap-y-2 text-sm w-full' },
            React.createElement('dt', { className: 'font-medium' }, 'QR version'),
            React.createElement('dd', null, String(result.metadata.version)),
            React.createElement('dt', { className: 'font-medium' }, 'Modules'),
            React.createElement('dd', null, String(result.metadata.moduleCount)),
            React.createElement('dt', { className: 'font-medium' }, 'Error correction'),
            React.createElement('dd', null,
              `${result.metadata.requestedErrorCorrection} → ${result.metadata.actualErrorCorrection}`
            ),
            React.createElement('dt', { className: 'font-medium' }, 'Scanability guard'),
            React.createElement('dd', null, result.metadata.scanability),
            React.createElement('dt', { className: 'font-medium' }, 'Suggested minimum'),
            React.createElement('dd', null, `${result.metadata.recommendedMinimumPixels}px square`)
          ),
          React.createElement('button', {
            type: 'button', onClick: downloadSVG,
            className: 'bg-green-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-green-700'
          }, 'Download SVG')
        )
      )
    )
  );
};

ReactDOM.render(React.createElement(App), document.getElementById('root'));
