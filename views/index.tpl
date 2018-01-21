<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title></title>
</head>
<body>

    <p>
        <a href="/">Back to home page</a>
        <a href="/end">Save to eBos</a>
        <a href="/new">Start new stocktake</a>
    </p>


    %for i in range(len(locationNames)):
        <ul>
            <li><a href="/area/{{safeNames[i]}}">{{locationNames[i]}}</a></li>
        </ul>
    %end

</body>
</html>