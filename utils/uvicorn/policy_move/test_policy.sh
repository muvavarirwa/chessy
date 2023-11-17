#!/bin/bash

# Basic while loop

url_1 = "http://localhost:9000/policy_move/?1&q=2&q=3&q=4&q=5&q=6&q=0&q=8&q=0&q=10&q=11&q=12&q=14&q=15&q=16&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=0&q=-1&q=-2&q=-3&q=-4&q=-5&q=-6&q=-7&q=-8&q=-9&q=-10&q=-11&q=-12&q=-14&q=-15&q=-16"


while true; do
    data=$(curl --request GET \
        --url $url_1 
        )
    [[    $data ]] || break
    echo "$data"  
done

echo All done

