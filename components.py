def get_flip_card_html(front_text, back_image_url=None, no_image_text="尚無照片"):
    """
    Generates HTML and CSS for a click-to-flip card.
    If back_image_url is provided, it displays the image on the back.
    Otherwise, it displays the no_image_text.
    """
    
    # We will generate a unique ID for each card to ensure JS toggles the right one.
    import uuid
    card_id = f"card_{uuid.uuid4().hex}"
    
    back_content = f"""
        <img src="{back_image_url}" alt="{front_text}" class="card-image" />
    """ if back_image_url else f"""
        <div class="no-image-text">{no_image_text}</div>
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
            background: #fafafa;
        }}
        .card-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
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

        <script>
            function flipCard(cardId) {{
                var card = document.getElementById(cardId);
                card.classList.toggle('is-flipped');
            }}
        </script>
    </body>
    </html>
    """
    
    return html_content
