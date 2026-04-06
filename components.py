import json

def get_flip_card_html(front_text, back_image_urls=None, no_image_text="尚無照片"):
    """
    Generates HTML and CSS for a click-to-flip card.
    If back_image_urls is provided (a list), it displays a random image on the back and randomizes on flip.
    Otherwise, it displays the no_image_text.
    """
    
    # We will generate a unique ID for each card and image to ensure JS toggles the right one.
    import uuid
    card_id = f"card_{uuid.uuid4().hex}"
    img_id = f"img_{uuid.uuid4().hex}"
    bg_id = f"bg_{uuid.uuid4().hex}"
    
    urls = back_image_urls if back_image_urls else []
    
    if not urls:
        back_content = f'<div class="no-image-text">{no_image_text}</div>'
        script_content = f"""
        <script>
            function flipCard(cardId) {{
                var card = document.getElementById(cardId);
                card.classList.toggle('is-flipped');
            }}
        </script>
        """
    else:
        back_content = f'''
        <div class="image-wrapper">
            <div id="{bg_id}" class="card-image-bg"></div>
            <img id="{img_id}" src="" alt="{front_text}" class="card-image-fg" />
        </div>
        '''
        urls_json = json.dumps(urls)
        script_content = f"""
        <script>
            var urls = {urls_json};
            var imgElement = document.getElementById('{img_id}');
            var bgElement = document.getElementById('{bg_id}');
            
            function getRandomUrl() {{
                return urls[Math.floor(Math.random() * urls.length)];
            }}
            
            function setImage(url) {{
                imgElement.src = url;
                bgElement.style.backgroundImage = "url('" + url + "')";
            }}
            
            // Set first random image on load
            if(urls.length > 0) {{
                setImage(getRandomUrl());
            }}

            function flipCard(cardId) {{
                var card = document.getElementById(cardId);
                var isFlipped = card.classList.contains('is-flipped');
                
                if (isFlipped) {{
                    card.classList.remove('is-flipped');
                    // Change the image while the back is facing away (halfway through the 0.6s animation)
                    setTimeout(function() {{
                        setImage(getRandomUrl());
                    }}, 300);
                }} else {{
                    card.classList.add('is-flipped');
                }}
            }}
        </script>
        """

    # We use a pure HTML/CSS/JS structure that can be embedded via st.components.v1.html
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: transparent;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .scene {{
            width: 100%;
            height: 300px;
            perspective: 1000px;
            cursor: pointer;
        }}
        .card {{
            width: 100%;
            height: 100%;
            position: relative;
            transition: transform 0.6s;
            transform-style: preserve-3d;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .card.is-flipped {{
            transform: rotateY(180deg);
        }}
        .card-face {{
            position: absolute;
            width: 100%;
            height: 100%;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            background: white;
            border: 1px solid #e0e0e0;
        }}
        .card-front {{
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
            color: #333;
            font-size: 1.2rem;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            box-sizing: border-box;
        }}
        .card-back {{
            transform: rotateY(180deg);
            background: #111;
            position: relative;
        }}
        .image-wrapper {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 12px;
        }}
        .card-image-bg {{
            position: absolute;
            top: -10%; left: -10%;
            width: 120%; height: 120%;
            background-size: cover;
            background-position: center;
            filter: blur(15px) brightness(0.6);
            z-index: 1;
        }}
        .card-image-fg {{
            position: relative;
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            z-index: 2;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }}
        .no-image-text {{
            color: #888;
            font-size: 1.2rem;
            font-style: italic;
        }}
    </style>
    </head>
    <body>
        <div class="scene" onclick="flipCard('{card_id}')">
            <div class="card" id="{card_id}">
                <div class="card-face card-front">
                    {front_text}
                </div>
                <div class="card-face card-back">
                    {back_content}
                </div>
            </div>
        </div>

        {script_content}
    </body>
    </html>
    """
    
    return html_content
