<?php 
/******
 * Author: Ethan Gruber
 * Date: February 2026
 * Function: This can iterate through multimple CSV files in a 'csv' folder located
 * in the directory of this PHP file. It will extract the descriptions from an array of column
 * headings as defined in the HEADINGS constant. The type descriptions are reduced to unique values
 * before exported to 'description.txt'. The text file can be loaded and parsed by generate_concept_list.py
 * for NLP
 */


$desc = array();
$files = scandir('csv');

define('HEADINGS', array('Obverse Type', 'Reverse Type'));

//iterate through CSV files
foreach($files as $file) {
    // Skip directories
    if (!is_dir($file)) {
        if (strpos($file, '.csv') !== FALSE) {
            $data = generate_json('csv/' . $file);
            extract_descriptions($data);
        }        
    }
}

asort($desc);

$fp = fopen("description.txt", "w");
foreach ($desc as $line) {
    fwrite($fp, $line . "\n");
}
fclose($fp);





function extract_descriptions($data) {
    GLOBAL $desc;
    
    foreach ($data as $row) {
        foreach ($row as $k=>$v) {
            $v = trim($v);
            
            //match values on pre-defined headings in the CSV file(s)
            if (in_array($k, HEADINGS)) {
                if (!in_array($v, $desc)) {
                   //insert distinct descriptions
                   $desc[] = $v;
                }
            }
        }
    }
}

function generate_json($doc){
    $keys = array();
    $geoData = array();
    
    $data = csvToArray($doc, ',');
    
    // Set number of elements (minus 1 because we shift off the first row)
    $count = count($data) - 1;
    
    //Use first row for names
    $labels = array_shift($data);
    
    foreach ($labels as $label) {
        $keys[] = $label;
    }
    
    // Bring it all together
    for ($j = 0; $j < $count; $j++) {
        $d = array_combine($keys, $data[$j]);
        $geoData[$j] = $d;
    }
    return $geoData;
}

// Function to convert CSV into associative array
function csvToArray($file, $delimiter) {
    if (($handle = fopen($file, 'r')) !== FALSE) {
        $i = 0;
        while (($lineArray = fgetcsv($handle, 4000, $delimiter, '"')) !== FALSE) {
            for ($j = 0; $j < count($lineArray); $j++) {
                $arr[$i][$j] = $lineArray[$j];
            }
            $i++;
        }
        fclose($handle);
    }
    return $arr;
}

?>