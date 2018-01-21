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
    </p>

    <h1 class = "areaHeader">{{area}}</h1>

    <table>
        <form>
            %for item in itemAttrib:
            <tr>
                <td>
                    <p class ="itemName">{{item['name']}}</p>
                    <p> <span class = "uom"> Unit of measurement {{item['uom']}}</span></p>
                </td>
            </tr>
            <tr>
                <td>
                    <span class = "caseUnits"> Case units {{item['caseUnits']}}</span>
                    <input class = "caseInput" type = "text" name = "{{item['wrinNo']}} caseCount" value="{{item['caseCount']}}" placeholder="Cases">
                </td>
            </tr>
            <tr>
                <td>
                    %if (item['sleeveUnits'] > 0):
                    <span class = "sleeveUnits"> Sleeve units {{item['sleeveUnits']}}</span>
                    <input class = "sleeveInput" type = "text" name = "{{item['wrinNo']}} sleeveCount" placeholder="Sleeves" value="{{item['sleeveCount']}}">
                    %end
                    %if (item['sleeveUnits'] == 0):
                    <span class = "sleeveUnits"></span>
                    <input class = "sleeveInput" type = "text" name = "{{item['wrinNo']}} sleeveCount" placeholder="Sleeves" value="{{item['sleeveCount']}}" disabled>
                    %end
                </td>
            </tr>
            <tr>
                <td>
                    <span class = "eachUnits"> Units</span>]
                    <input class = "eachInput" type = "text" name = "{{item['wrinNo']}} looseCount" placeholder="Each" value="{{item['looseCount']}}">
                </td>
            </tr>
            %end
            <button type='submit' onclick='stockSubmit.tpl' formmethod="post"> Submit </button>
        </form>
    </table>

</body>
</html>