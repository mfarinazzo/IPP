<?php
// Inclui a conex�o com o banco de dados
$servername = "localhost";
$username = "plata287";
$password = "TjlF52yoyu9nvj-_5u";
$dbname = "plataformatour_PI";
$flag = false;

$conn = new mysqli($servername, $username, $password, $dbname);

// Fun��o para escrever no arquivo de log
function write_log($message) {
    $logfile = 'log.txt';
    $current = file_get_contents($logfile);
    $current .= date('Y-m-d H:i:s') . " - " . $message . "\n";
    file_put_contents($logfile, $current);
}

// Fun��o para escrever no arquivo de log de depura��o
function write_debug_log($message) {
    $logfile = 'debug_log.txt';
    $current = file_get_contents($logfile);
    $current .= date('Y-m-d H:i:s') . " - " . $message . "\n";
    file_put_contents($logfile, $current);
}

// Verificar conex�o
if ($conn->connect_error) {
    $error_message = "Falha na conex�o: " . $conn->connect_error;
    write_log($error_message);
    write_debug_log($error_message);
    die(json_encode(['status' => 'error', 'message' => $error_message]));
}

// Verificar se dados foram recebidos
$input = file_get_contents('php://input');
write_log("Dados recebidos: " . $input);
write_debug_log("Dados recebidos: " . $input);

$data = json_decode($input, true);

if ($data && is_array($data)) {
    $conn->begin_transaction();

    try {
        $values = [];
        $types = '';
        $placeholders = [];

        foreach ($data as $row) {
            $id = $row['id'] ?? null;
            if(isset($row['subclasse'])){
                $cnae = $row['subclasse'];
            } else {
                $flag = true;
                $cnae = $row['ocupacao'] ?? null;
            }
            $media_salarial_geral = $row['media_salarial_geral'] ?? null;
            $idade18 = $row['18-29'] ?? null;
            $idade30 = $row['30-39'] ?? null;
            $idade40 = $row['40-49'] ?? null;
            $idade50 = $row['50-59'] ?? null;
            $idade60 = $row['60+'] ?? null;
            $media_idade_geral = $row['media_idade_geral'] ?? null;
            $municipio = $row['municipio'] ?? null;
            $data = $row['data'] ?? null;

            // Garantir que a data esteja no formato correto
            $data = date('Y-m-d', strtotime($data));

            $values[] = $id;
            $values[] = $cnae;
            $values[] = $media_salarial_geral;
            $values[] = $idade18;
            $values[] = $idade30;
            $values[] = $idade40;
            $values[] = $idade50;
            $values[] = $idade60;
            $values[] = $media_idade_geral;
            $values[] = $municipio;
            $values[] = $data;

            $types .= 'issssssssss';
            $placeholders[] = '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)';
        }

        write_debug_log("Valores constru�dos: " . print_r($values, true));
        write_debug_log("Tipos constru�dos: " . $types);
        write_debug_log("Flag value: " . ($flag ? "true" : "false"));

        $placeholders = implode(', ', $placeholders);
        write_debug_log("Placeholder query: " . $placeholders);

        if ($flag == false) {
            $query = "INSERT INTO PI_fornecedores_cnaes_municipio (id, cnae, media_salario, `18-29`, `30-39`, `40-49`, `50-59`, `60+`, media_idade, municipio, date) VALUES $placeholders";
        } else {
            $query = "INSERT INTO PI_fornecedores_ocupacoes_municipio (id, ocupacao, media_salario, `18-29`, `30-39`, `40-49`, `50-59`, `60+`, media_idade, municipio, date) VALUES $placeholders";
        }

        write_debug_log("Query: " . $query);

        $stmt = $conn->prepare($query);

        if (!$stmt) {
            $error_message = "Erro na prepara��o da query: " . $conn->error;
            write_log($error_message);
            write_debug_log($error_message);
            throw new Exception($error_message);
        }

        $stmt->bind_param($types, ...$values);

        write_debug_log("Valores para bind_param: " . print_r($values, true));

        if (!$stmt->execute()) {
            $error_message = $stmt->error;
            write_log($error_message);
            write_debug_log($error_message);
            throw new Exception($error_message);
        }

        $conn->commit();
        $success_message = "Dados inseridos com sucesso!";
        write_log($success_message);
        write_debug_log($success_message);
        echo json_encode(['status' => 'success', 'message' => $success_message]);
    } catch (Exception $e) {
        $conn->rollback();
        $error_message = "Erro ao inserir dados: " . $e->getMessage();
        write_log($error_message);
        write_debug_log($error_message);
        echo json_encode(['status' => 'error', 'message' => $error_message]);
    }
} else {
    $error_message = "Nenhum dado recebido ou erro ao decodificar JSON.";
    write_log($error_message);
    write_debug_log($error_message);
    echo json_encode(['status' => 'error', 'message' => $error_message]);
}

$conn->close();
?>
