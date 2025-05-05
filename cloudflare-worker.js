addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const path = url.pathname
  
  // Handle both root path and callback path
  if (path === '/' || path === '/callback') {
    const code = url.searchParams.get('code')
    const jsonBlobId = '1286814164436508672'  // Using the ID from your environment

    if (!code) {
      return new Response('Hey! This is SpotifyNow\'s authentication server.', { 
        status: 200,
        headers: {
          'Content-Type': 'text/html',
        }
      })
    }

    const key = code.slice(-4)
    const redirectURL = `http://t.me/fullmetaltestbot/?start=${key}`

    try {
      // Fetch the current blob content first
      const blobResponse = await fetch(`https://jsonblob.com/api/${jsonBlobId}`)
      let blobData = {}
      
      // If blob exists, use its content
      if (blobResponse.ok) {
        try {
          blobData = await blobResponse.json()
        } catch (e) {
          console.error('Error parsing JSON blob:', e)
          // Continue with empty object if parsing fails
        }
      }
      
      // Add the new code to the blob
      blobData[key] = code
      
      // Update the blob
      await fetch(`https://jsonblob.com/api/${jsonBlobId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(blobData),
      })
      
      return Response.redirect(redirectURL, 302)
    } catch (error) {
      console.error('Error handling authentication:', error)
      return new Response('Authentication error. Please try again.', { status: 500 })
    }
  }
  
  // Handle all other paths
  return new Response('Not found', { status: 404 })
} 