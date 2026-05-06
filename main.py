from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

SAVE_DIR = "pic"
os.makedirs(SAVE_DIR, exist_ok=True)

HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>局域网图片上传</title>
</head>

<body style="font-family:sans-serif;padding:40px">

<h2>批量上传图片</h2>

<input type="file" id="file" multiple><br><br>

压缩比例：
<select id="scale">
    <option value="1">不压缩</option>
    <option value="0.5">50%</option>
    <option value="0.3">30%</option>
    <option value="0.1">10%</option>
</select>

<button onclick="upload()">上传</button>

<p id="msg"></p>

<progress id="progress" value="0" max="100"
style="width:300px"></progress>

<script>

async function compress(file, ratio){

    if(ratio == 1) return file;

    let targetSize = file.size * ratio;

    return new Promise(resolve => {

        let img = new Image();
        let reader = new FileReader();

        reader.onload = e => img.src = e.target.result;

        img.onload = () => {

            let canvas = document.createElement("canvas");

            canvas.width = img.width;
            canvas.height = img.height;

            canvas.getContext("2d")
                  .drawImage(img, 0, 0);

            let quality = 0.9;

            function tryCompress(){

                canvas.toBlob(blob => {

                    if(blob.size <= targetSize || quality <= 0.05){

                        resolve(new File(
                            [blob],
                            file.name,
                            {type:"image/jpeg"}
                        ));

                    }else{

                        quality -= 0.05;
                        tryCompress();

                    }

                }, "image/jpeg", quality);
            }

            tryCompress();
        };

        reader.readAsDataURL(file);
    });
}

async function sendFile(file){

    return new Promise(resolve => {

        let form = new FormData();
        form.append("file", file);

        let xhr = new XMLHttpRequest();

        xhr.upload.onprogress = e => {

            if(e.lengthComputable){

                let p = Math.round(
                    e.loaded / e.total * 100
                );

                document.getElementById("progress")
                        .value = p;
            }
        };

        xhr.onload = () => resolve();

        xhr.open("POST", "/upload");
        xhr.send(form);
    });
}

async function upload(){

    let files = document.getElementById("file").files;

    if(files.length == 0){
        alert("请选择图片");
        return;
    }

    let ratio = parseFloat(
        document.getElementById("scale").value
    );

    for(let i = 0; i < files.length; i++){

        let f = files[i];

        document.getElementById("msg")
                .innerText =
                `压缩 ${i+1}/${files.length}`;

        let c = await compress(f, ratio);

        document.getElementById("msg")
                .innerText =
                `上传 ${i+1}/${files.length}`;

        document.getElementById("progress")
                .value = 0;

        await sendFile(c);
    }

    document.getElementById("msg")
            .innerText = "全部上传完成";

    document.getElementById("progress")
            .value = 100;
}

</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/upload", methods=["POST"])
def upload():

    f = request.files["file"]

    f.save(os.path.join(SAVE_DIR, f.filename))

    return "ok"

app.run(host="0.0.0.0", port=5000)