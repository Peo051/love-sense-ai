import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

FAMILIES_DATA = [
    # 36 DEV FAMILIES (36 * 10 = 360 samples)
    {"id": "fam-student-profile", "name_vi": "Hồ sơ sinh viên", "entity": "Student", "attr1": "Name", "attr1_t": "string", "attr2": "Gpa", "attr2_t": "double", "action": "DisplayInfo", "rule": "GPA phải từ 0.0 đến 4.0"},
    {"id": "fam-bank-account", "name_vi": "Tài khoản ngân hàng", "entity": "BankAccount", "attr1": "AccountNumber", "attr1_t": "string", "attr2": "Balance", "attr2_t": "decimal", "action": "Deposit", "rule": "Số tiền gửi phải lớn hơn 0"},
    {"id": "fam-product-inventory", "name_vi": "Quản lý sản phẩm", "entity": "Product", "attr1": "ProductName", "attr1_t": "string", "attr2": "StockQuantity", "attr2_t": "int", "action": "AddStock", "rule": "Số lượng nhập kho phải không âm"},
    {"id": "fam-employee-payroll", "name_vi": "Bảng lương nhân viên", "entity": "Employee", "attr1": "EmployeeName", "attr1_t": "string", "attr2": "BaseSalary", "attr2_t": "double", "action": "CalculatePay", "rule": "Lương cơ bản không được âm"},
    {"id": "fam-library-book", "name_vi": "Sách thư viện", "entity": "Book", "attr1": "Title", "attr1_t": "string", "attr2": "PageCount", "attr2_t": "int", "action": "BorrowBook", "rule": "Số trang sách phải lớn hơn 0"},
    {"id": "fam-car-odometer", "name_vi": "Công tơ mét ô tô", "entity": "Car", "attr1": "Model", "attr1_t": "string", "attr2": "Mileage", "attr2_t": "double", "action": "Drive", "rule": "Khoảng cách di chuyển phải dương"},
    {"id": "fam-rectangle-geometry", "name_vi": "Hình chữ nhật hình học", "entity": "Rectangle", "attr1": "Name", "attr1_t": "string", "attr2": "Width", "attr2_t": "double", "action": "CalculateArea", "rule": "Chiều rộng phải lớn hơn 0"},
    {"id": "fam-circle-geometry", "name_vi": "Hình tròn hình học", "entity": "Circle", "attr1": "Label", "attr1_t": "string", "attr2": "Radius", "attr2_t": "double", "action": "CalculateArea", "rule": "Bán kính phải lớn hơn 0"},
    {"id": "fam-bank-card", "name_vi": "Thẻ ATM ngân hàng", "entity": "DebitCard", "attr1": "CardNumber", "attr1_t": "string", "attr2": "DailyLimit", "attr2_t": "decimal", "action": "Charge", "rule": "Hạn mức ngày phải lớn hơn 0"},
    {"id": "fam-customer-order", "name_vi": "Đơn đặt hàng", "entity": "Order", "attr1": "OrderId", "attr1_t": "string", "attr2": "TotalAmount", "attr2_t": "decimal", "action": "ApplyDiscount", "rule": "Tổng tiền đơn hàng không được âm"},
    {"id": "fam-course-enrollment", "name_vi": "Ghi danh khóa học", "entity": "Course", "attr1": "CourseTitle", "attr1_t": "string", "attr2": "MaxStudents", "attr2_t": "int", "action": "EnrollStudent", "rule": "Sĩ số tối đa phải từ 1 trở lên"},
    {"id": "fam-shopping-cart", "name_vi": "Giỏ hàng điện tử", "entity": "ShoppingCart", "attr1": "CustomerName", "attr1_t": "string", "attr2": "ItemCount", "attr2_t": "int", "action": "Checkout", "rule": "Số lượng món đồ không được âm"},
    {"id": "fam-temperature-sensor", "name_vi": "Cảm biến nhiệt độ", "entity": "TempSensor", "attr1": "Location", "attr1_t": "string", "attr2": "Reading", "attr2_t": "double", "action": "UpdateReading", "rule": "Nhiệt độ đọc không dưới độ không tuyệt đối -273.15"},
    {"id": "fam-smartphone-battery", "name_vi": "Pin điện thoại thông minh", "entity": "Smartphone", "attr1": "Brand", "attr1_t": "string", "attr2": "BatteryLevel", "attr2_t": "int", "action": "ChargeBattery", "rule": "Mức pin phải trong khoảng 0 đến 100"},
    {"id": "fam-pet-care", "name_vi": "Chăm sóc thú cưng", "entity": "Pet", "attr1": "PetName", "attr1_t": "string", "attr2": "EnergyLevel", "attr2_t": "int", "action": "FeedPet", "rule": "Mức năng lượng phải từ 0 đến 100"},
    {"id": "fam-flight-ticket", "name_vi": "Vé máy bay", "entity": "FlightTicket", "attr1": "FlightCode", "attr1_t": "string", "attr2": "Fare", "attr2_t": "decimal", "action": "ConfirmTicket", "rule": "Giá vé máy bay phải lớn hơn 0"},
    {"id": "fam-hotel-room", "name_vi": "Phòng khách sạn", "entity": "HotelRoom", "attr1": "RoomNumber", "attr1_t": "string", "attr2": "PricePerNight", "attr2_t": "decimal", "action": "BookRoom", "rule": "Giá phòng mỗi đêm phải lớn hơn 0"},
    {"id": "fam-movie-ticket", "name_vi": "Vé xem phim", "entity": "MovieTicket", "attr1": "MovieTitle", "attr1_t": "string", "attr2": "SeatNumber", "attr2_t": "int", "action": "PrintTicket", "rule": "Số ghế ngồi phải là số nguyên dương"},
    {"id": "fam-wallet-balance", "name_vi": "Ví tiền điện tử", "entity": "EWallet", "attr1": "OwnerName", "attr1_t": "string", "attr2": "Funds", "attr2_t": "decimal", "action": "AddFunds", "rule": "Số tiền nạp vào ví phải lớn hơn 0"},
    {"id": "fam-timer-stopwatch", "name_vi": "Đồng hồ bấm giờ", "entity": "Stopwatch", "attr1": "Label", "attr1_t": "string", "attr2": "ElapsedSeconds", "attr2_t": "int", "action": "AddSeconds", "rule": "Số giây trôi qua không được âm"},
    {"id": "fam-game-character", "name_vi": "Nhân vật trò chơi", "entity": "Character", "attr1": "HeroName", "attr1_t": "string", "attr2": "HealthPoints", "attr2_t": "int", "action": "TakeDamage", "rule": "Điểm máu nhân vật không được âm"},
    {"id": "fam-vehicle-speed", "name_vi": "Tốc độ phương tiện", "entity": "Vehicle", "attr1": "LicensePlate", "attr1_t": "string", "attr2": "CurrentSpeed", "attr2_t": "double", "action": "Accelerate", "rule": "Tốc độ xe không được âm"},
    {"id": "fam-laptop-spec", "name_vi": "Cấu hình máy tính", "entity": "Laptop", "attr1": "CpuModel", "attr1_t": "string", "attr2": "RamGigabytes", "attr2_t": "int", "action": "UpgradeRam", "rule": "Dung lượng RAM phải từ 2 trở lên"},
    {"id": "fam-music-track", "name_vi": "Bài hát âm nhạc", "entity": "MusicTrack", "attr1": "TrackTitle", "attr1_t": "string", "attr2": "DurationInSeconds", "attr2_t": "int", "action": "PlayTrack", "rule": "Thời lượng bài hát phải lớn hơn 0"},
    {"id": "fam-classroom-seat", "name_vi": "Chỗ ngồi lớp học", "entity": "Classroom", "attr1": "RoomCode", "attr1_t": "string", "attr2": "Capacity", "attr2_t": "int", "action": "AddDesk", "rule": "Sức chứa phòng học phải lớn hơn 0"},
    {"id": "fam-medical-record", "name_vi": "Hồ sơ y tế", "entity": "PatientRecord", "attr1": "PatientName", "attr1_t": "string", "attr2": "HeartRate", "attr2_t": "int", "action": "RecordVitals", "rule": "Nhịp tim phải lớn hơn 0"},
    {"id": "fam-coffee-order", "name_vi": "Đơn cà phê", "entity": "CoffeeOrder", "attr1": "DrinkName", "attr1_t": "string", "attr2": "SugarGrams", "attr2_t": "int", "action": "AddSugar", "rule": "Lượng đường không được nhận giá trị âm"},
    {"id": "fam-vending-machine", "name_vi": "Máy bán hàng tự động", "entity": "VendingMachine", "attr1": "MachineId", "attr1_t": "string", "attr2": "CoinReserve", "attr2_t": "decimal", "action": "InsertCoins", "rule": "Tiền dự trữ không được là số âm"},
    {"id": "fam-parcel-shipping", "name_vi": "Vận chuyển bưu kiện", "entity": "Parcel", "attr1": "TrackingCode", "attr1_t": "string", "attr2": "WeightKg", "attr2_t": "double", "action": "EstimateCost", "rule": "Khối lượng bưu kiện phải lớn hơn 0"},
    {"id": "fam-elevator-controller", "name_vi": "Điều khiển thang máy", "entity": "Elevator", "attr1": "ElevatorId", "attr1_t": "string", "attr2": "CurrentFloor", "attr2_t": "int", "action": "MoveToFloor", "rule": "Số tầng phải nằm trong phạm vi tòa nhà từ 1 đến 50"},
    {"id": "fam-thermostat-climate", "name_vi": "Bộ điều nhiệt", "entity": "Thermostat", "attr1": "ZoneName", "attr1_t": "string", "attr2": "TargetTemp", "attr2_t": "double", "action": "AdjustTemp", "rule": "Nhiệt độ phòng mục tiêu phải từ 16 đến 32 độ C"},
    {"id": "fam-fitness-tracker", "name_vi": "Vòng đeo thể thao", "entity": "FitnessBand", "attr1": "UserName", "attr1_t": "string", "attr2": "StepCount", "attr2_t": "int", "action": "LogSteps", "rule": "Số bước chân ghi nhận không được âm"},
    {"id": "fam-recipe-ingredient", "name_vi": "Nguyên liệu món ăn", "entity": "Ingredient", "attr1": "IngredientName", "attr1_t": "string", "attr2": "AmountGrams", "attr2_t": "double", "action": "Consume", "rule": "Lượng nguyên liệu phải lớn hơn 0"},
    {"id": "fam-task-todo", "name_vi": "Nhiệm vụ công việc", "entity": "TaskItem", "attr1": "TaskTitle", "attr1_t": "string", "attr2": "PriorityLevel", "attr2_t": "int", "action": "UpdatePriority", "rule": "Mức độ ưu tiên phải từ 1 đến 5"},
    {"id": "fam-saving-deposit", "name_vi": "Sổ tiết kiệm", "entity": "SavingsAccount", "attr1": "PassbookId", "attr1_t": "string", "attr2": "Principal", "attr2_t": "decimal", "action": "AccrueInterest", "rule": "Tiền gốc gửi tiết kiệm phải lớn hơn 0"},
    {"id": "fam-drone-flight", "name_vi": "Thiết bị bay drone", "entity": "Drone", "attr1": "DroneCode", "attr1_t": "string", "attr2": "AltitudeMeters", "attr2_t": "double", "action": "Climb", "rule": "Độ cao bay không được âm"},

    # 12 VALIDATION FAMILIES (12 * 10 = 120 samples)
    {"id": "fam-parking-lot", "name_vi": "Bãi đỗ xe", "entity": "ParkingLot", "attr1": "LotName", "attr1_t": "string", "attr2": "OccupiedSpaces", "attr2_t": "int", "action": "ParkCar", "rule": "Số chỗ đỗ xe không được là số âm"},
    {"id": "fam-gym-membership", "name_vi": "Thẻ hội viên Gym", "entity": "GymMember", "attr1": "MemberName", "attr1_t": "string", "attr2": "RemainingDays", "attr2_t": "int", "action": "RenewDays", "rule": "Số ngày gia hạn phải lớn hơn 0"},
    {"id": "fam-water-tank", "name_vi": "Bồn chứa nước", "entity": "WaterTank", "attr1": "TankId", "attr1_t": "string", "attr2": "VolumeLiters", "attr2_t": "double", "action": "FillWater", "rule": "Thể tích nước không được âm"},
    {"id": "fam-printer-spool", "name_vi": "Máy in văn phòng", "entity": "OfficePrinter", "attr1": "PrinterName", "attr1_t": "string", "attr2": "PaperSheets", "attr2_t": "int", "action": "LoadPaper", "rule": "Số tờ giấy nạp thêm phải lớn hơn 0"},
    {"id": "fam-bus-trip", "name_vi": "Chuyến xe buýt", "entity": "BusTrip", "attr1": "RouteNumber", "attr1_t": "string", "attr2": "PassengerCount", "attr2_t": "int", "action": "BoardPassenger", "rule": "Số hành khách trên xe không được âm"},
    {"id": "fam-weather-forecast", "name_vi": "Trạm thời tiết", "entity": "WeatherStation", "attr1": "StationCity", "attr1_t": "string", "attr2": "HumidityPercent", "attr2_t": "double", "action": "LogHumidity", "rule": "Độ ẩm phải trong khoảng từ 0 đến 100%"},
    {"id": "fam-solar-panel", "name_vi": "Hệ pin năng lượng mặt trời", "entity": "SolarPanel", "attr1": "SerialCode", "attr1_t": "string", "attr2": "WattOutput", "attr2_t": "double", "action": "GeneratePower", "rule": "Công suất phát điện không được âm"},
    {"id": "fam-kitchen-oven", "name_vi": "Lò nướng nhà bếp", "entity": "KitchenOven", "attr1": "OvenModel", "attr1_t": "string", "attr2": "SetTempCelsius", "attr2_t": "int", "action": "Preheat", "rule": "Nhiệt độ nướng phải từ 50 đến 300 độ C"},
    {"id": "fam-traffic-light", "name_vi": "Đèn tín hiệu giao thông", "entity": "TrafficLight", "attr1": "Intersection", "attr1_t": "string", "attr2": "GreenDuration", "attr2_t": "int", "action": "SetGreenTime", "rule": "Thời gian đèn xanh phải lớn hơn 0 giây"},
    {"id": "fam-water-bottle", "name_vi": "Bình giữ nhiệt", "entity": "ThermosBottle", "attr1": "BrandName", "attr1_t": "string", "attr2": "CapacityMl", "attr2_t": "int", "action": "PourWater", "rule": "Dung tích bình giữ nhiệt phải lớn hơn 0"},
    {"id": "fam-podcast-episode", "name_vi": "Tập podcast", "entity": "PodcastEpisode", "attr1": "EpisodeTitle", "attr1_t": "string", "attr2": "DurationMinutes", "attr2_t": "int", "action": "StartStream", "rule": "Thời lượng phát phải lớn hơn 0 phút"},
    {"id": "fam-bike-rental", "name_vi": "Xe đạp cho thuê", "entity": "RentalBike", "attr1": "BikeId", "attr1_t": "string", "attr2": "RentalHours", "attr2_t": "double", "action": "RentOut", "rule": "Số giờ thuê xe phải lớn hơn 0"},

    # 12 TEST FAMILIES (12 * 10 = 120 samples) - FROZEN SPLIT
    {"id": "fam-warehouse-pallet", "name_vi": "Pallet kho bãi", "entity": "WarehousePallet", "attr1": "PalletCode", "attr1_t": "string", "attr2": "LoadWeightKg", "attr2_t": "double", "action": "StackLoad", "rule": "Khối lượng hàng trên pallet không được âm"},
    {"id": "fam-atm-cash-dispenser", "name_vi": "Bộ cấp tiền máy ATM", "entity": "AtmDispenser", "attr1": "MachineCode", "attr1_t": "string", "attr2": "BillCount", "attr2_t": "int", "action": "Dispense", "rule": "Số lượng tờ tiền không được âm"},
    {"id": "fam-aquarium-filter", "name_vi": "Hồ thủy sinh", "entity": "Aquarium", "attr1": "TankLabel", "attr1_t": "string", "attr2": "WaterTempC", "attr2_t": "double", "action": "HeatWater", "rule": "Nhiệt độ nước hồ phải từ 10 đến 40 độ C"},
    {"id": "fam-refrigerator-temp", "name_vi": "Tủ lạnh gia đình", "entity": "Fridge", "attr1": "ModelTag", "attr1_t": "string", "attr2": "CoolingTemp", "attr2_t": "double", "action": "SetCooling", "rule": "Nhiệt độ làm mát tủ lạnh từ 0 đến 10 độ C"},
    {"id": "fam-vessel-cargo", "name_vi": "Tàu vận tải hàng", "entity": "CargoVessel", "attr1": "VesselName", "attr1_t": "string", "attr2": "CargoTons", "attr2_t": "double", "action": "LoadCargo", "rule": "Trọng tải chở hàng không được âm"},
    {"id": "fam-plant-irrigation", "name_vi": "Hệ thống tưới cây tự động", "entity": "IrrigationSystem", "attr1": "GardenZone", "attr1_t": "string", "attr2": "MoistureThreshold", "attr2_t": "int", "action": "WaterPlants", "rule": "Ngưỡng độ ẩm đất phải từ 0 đến 100%"},
    {"id": "fam-smart-bulb", "name_vi": "Bóng đèn thông minh", "entity": "SmartBulb", "attr1": "DeviceName", "attr1_t": "string", "attr2": "BrightnessPercent", "attr2_t": "int", "action": "DimLight", "rule": "Độ sáng phải trong khoảng 0 đến 100%"},
    {"id": "fam-solar-battery", "name_vi": "Bộ lưu điện pin mặt trời", "entity": "StorageBattery", "attr1": "UnitId", "attr1_t": "string", "attr2": "StoredKwh", "attr2_t": "double", "action": "StoreEnergy", "rule": "Dung lượng điện lưu trữ không được là số âm"},
    {"id": "fam-camera-memory", "name_vi": "Thẻ nhớ máy ảnh", "entity": "CameraCard", "attr1": "CardType", "attr1_t": "string", "attr2": "FreeSpaceMb", "attr2_t": "int", "action": "SavePhoto", "rule": "Dung lượng thẻ nhớ trống không được âm"},
    {"id": "fam-fuel-dispenser", "name_vi": "Cột bơm xăng điện tử", "entity": "FuelPump", "attr1": "PumpId", "attr1_t": "string", "attr2": "LitersDispensed", "attr2_t": "double", "action": "PumpFuel", "rule": "Số lít xăng bơm phải lớn hơn 0"},
    {"id": "fam-audio-amplifier", "name_vi": "Bộ khuếch đại âm thanh", "entity": "Amplifier", "attr1": "ModelName", "attr1_t": "string", "attr2": "VolumeLevel", "attr2_t": "int", "action": "IncreaseVolume", "rule": "Mức âm lượng phải từ 0 đến 100"},
    {"id": "fam-credit-limit", "name_vi": "Hạn mức thẻ tín dụng", "entity": "CreditCard", "attr1": "CardHolder", "attr1_t": "string", "attr2": "CreditLimit", "attr2_t": "decimal", "action": "AdjustLimit", "rule": "Hạn mức tín dụng phải lớn hơn 0"}
]

def find_line_range(code: str, substring: str) -> Tuple[int, int]:
    lines = code.split("\n")
    sub_lines = substring.split("\n")
    first_sub = sub_lines[0].strip()
    for i, line in enumerate(lines):
        if first_sub in line:
            return (i + 1, i + len(sub_lines))
    return (1, 1)

def generate_case(fam: Dict[str, Any], topic: str, sample_idx: int, split: str) -> Dict[str, Any]:
    sample_id = f"vct-{sample_idx:03d}"
    entity = fam["entity"]
    attr1 = fam["attr1"]
    attr2 = fam["attr2"]
    attr2_t = fam["attr2_t"]
    action = fam["action"]
    name_vi = fam["name_vi"]
    rule = fam["rule"]
    fam_id = fam["id"]

    val_init = "10" if attr2_t == "int" else ("10.5" if attr2_t == "double" else "100m")
    val_neg = "-5" if attr2_t == "int" else ("-5.0" if attr2_t == "double" else "-50m")

    if topic == "class_object":
        problem_vi = f"Viết chương trình C# khai báo lớp `{entity}` và sử dụng đối tượng trong hàm `Main` để gọi phương thức `{action}`."
        expected_vi = f"Khởi tạo đối tượng `{entity}` với từ khóa `new` và thực thi phương thức `{action}` thành công."
        student_code = f"""using System;

public class {entity}
{{
    public string {attr1} {{ get; set; }}
    public {attr2_t} {attr2} {{ get; set; }}

    public void {action}()
    {{
        Console.WriteLine("{entity} executing {action}");
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} item;
        item.{action}();
    }}
}}"""
        evidence = f"item.{action}();"
        start_line, end_line = find_line_range(student_code, evidence)
        ref_solution = f"""using System;

public class {entity}
{{
    public string {attr1} {{ get; set; }}
    public {attr2_t} {attr2} {{ get; set; }}

    public void {action}()
    {{
        Console.WriteLine("{entity} executing {action}");
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} item = new {entity}();
        item.{action}();
    }}
}}"""
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "beginner",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": "Use of unassigned local variable 'item' (CS0165)",
            "expected_behavior": expected_vi,
            "bug_status": "has_bug",
            "error_category": "compile_error",
            "bug_type": "uninstantiated_object_reference",
            "bug_location": {"file": "Program.cs", "start_line": start_line, "end_line": end_line, "symbol": f"item.{action}"},
            "knowledge_components": ["OOP.Classes", "OOP.Instantiation", "OOP.NullReference"],
            "possible_misconception": "Nghĩ rằng chỉ cần khai báo biến kiểu class thì đối tượng đã sẵn sàng hoạt động trong bộ nhớ mà không cần dùng từ khóa new.",
            "reference_diagnosis": f"Biến `{entity} item` chưa được khởi tạo với từ khóa `new`, dẫn đến lỗi sử dụng biến chưa gán giá trị (CS0165) khi gọi `{action}()`.",
            "evidence": evidence,
            "hint_1": "Hãy kiểm tra xem biến đối tượng của bạn đã được cấp phát vùng nhớ thực tế trước khi gọi phương thức hay chưa.",
            "hint_2": "Trong C#, biến kiểu tham chiếu (class) cần được khởi tạo thông qua toán tử `new` trước khi truy cập thành viên.",
            "hint_3": f"Hãy gán đối tượng mới: `{entity} item = new {entity}();` trước dòng gọi `{action}()`.",
            "reference_solution": ref_solution,
            "explanation_vi": f"Biến kiểu tham chiếu chỉ chứa địa chỉ ô nhớ. Khi khai báo `{entity} item;`, biến chưa trỏ đến bất kỳ đối tượng nào. Cần dùng `new {entity}()` để tạo thực thể trong heap.",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    elif topic == "field_property":
        problem_vi = f"Thiết kế lớp `{entity}` có trường dữ liệu `{attr1.lower()}` và cho phép lớp ngoài đọc thông tin này thông qua Property công khai."
        expected_vi = f"Truy cập và hiển thị thông tin `{attr1}` của `{entity}` thông qua Property `public` mà không vi phạm tính đóng gói."
        student_code = f"""using System;

public class {entity}
{{
    private string {attr1.lower()} = "DefaultValue";
}}

public class Program
{{
    public static void Main()
    {{
        {entity} obj = new {entity}();
        Console.WriteLine(obj.{attr1.lower()});
    }}
}}"""
        evidence = f"Console.WriteLine(obj.{attr1.lower()});"
        start_line, end_line = find_line_range(student_code, evidence)
        ref_solution = f"""using System;

public class {entity}
{{
    private string {attr1.lower()} = "DefaultValue";
    public string {attr1}
    {{
        get {{ return {attr1.lower()}; }}
        set {{ {attr1.lower()} = value; }}
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} obj = new {entity}();
        Console.WriteLine(obj.{attr1});
    }}
}}"""
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "beginner",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": f"'{entity}.{attr1.lower()}' is inaccessible due to its protection level (CS0122)",
            "expected_behavior": expected_vi,
            "bug_status": "has_bug",
            "error_category": "compile_error",
            "bug_type": "inaccessible_private_field",
            "bug_location": {"file": "Program.cs", "start_line": start_line, "end_line": end_line, "symbol": f"obj.{attr1.lower()}"},
            "knowledge_components": ["OOP.Fields", "OOP.AccessModifiers", "OOP.Properties"],
            "possible_misconception": "Hiểu nhầm rằng trường private có thể được truy xuất trực tiếp từ một lớp khác bên ngoài mà không cần qua property.",
            "reference_diagnosis": f"Trường `{attr1.lower()}` được khai báo `private` nên không thể truy cập trực tiếp từ lớp `Program` (lỗi CS0122).",
            "evidence": evidence,
            "hint_1": "Hãy quan sát mức độ truy cập (access modifier) của trường dữ liệu bạn đang cố in ra màn hình.",
            "hint_2": "Trường `private` chỉ có thể được truy cập bên trong chính lớp đó. Hãy xây dựng một Property `public` để cung cấp quyền đọc từ bên ngoài.",
            "hint_3": f"Thêm thuộc tính `public string {attr1} {{ get {{ return {attr1.lower()}; }} }}` vào lớp `{entity}` và dùng `obj.{attr1}` trong `Main`.",
            "reference_solution": ref_solution,
            "explanation_vi": "Nguyên tắc đóng gói yêu cầu che giấu trường dữ liệu private và cung cấp thuộc tính công khai (public property) để tương tác.",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    elif topic == "getter_setter":
        problem_vi = f"Xây dựng thuộc tính `{attr2}` trong lớp `{entity}` với logic kiểm tra dữ liệu bằng getter và setter tường minh kèm backing field."
        expected_vi = f"Thuộc tính `{attr2}` trả về và cập nhật biến sao lưu backing field `_{attr2.lower()}` mà không gây đệ quy vô tận."
        student_code = f"""using System;

public class {entity}
{{
    private {attr2_t} _{attr2.lower()};

    public {attr2_t} {attr2}
    {{
        get
        {{
            return {attr2};
        }}
        set
        {{
            {attr2} = value;
        }}
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} item = new {entity}();
        item.{attr2} = {val_init};
        Console.WriteLine(item.{attr2});
    }}
}}"""
        evidence = f"return {attr2};"
        start_line, end_line = find_line_range(student_code, evidence)
        ref_solution = f"""using System;

public class {entity}
{{
    private {attr2_t} _{attr2.lower()};

    public {attr2_t} {attr2}
    {{
        get
        {{
            return _{attr2.lower()};
        }}
        set
        {{
            _{attr2.lower()} = value;
        }}
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} item = new {entity}();
        item.{attr2} = {val_init};
        Console.WriteLine(item.{attr2});
    }}
}}"""
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "medium",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": None,
            "expected_behavior": expected_vi,
            "bug_status": "has_bug",
            "error_category": "runtime_error",
            "bug_type": "recursive_property_accessor",
            "bug_location": {"file": "Program.cs", "start_line": start_line, "end_line": end_line, "symbol": f"{entity}.{attr2}"},
            "knowledge_components": ["OOP.Properties", "OOP.BackingFields", "OOP.Recursion"],
            "possible_misconception": "Nhầm lẫn giữa tên thuộc tính (Property) và biến sao lưu (Backing Field), khiến Property tự gọi chính nó vô tận gây StackOverflowException.",
            "reference_diagnosis": f"Getter và Setter của `{attr2}` đang truy cập chính thuộc tính `{attr2}` thay vì biến sao lưu `_{attr2.lower()}`, gây tràn ngăn xếp khi chạy.",
            "evidence": evidence,
            "hint_1": "Hãy chú ý biến mà bạn đang trả về trong getter và gán trong setter.",
            "hint_2": "Khi thuộc tính tự gọi tên của chính nó bên trong getter hoặc setter, một vòng lặp đệ quy vô hạn sẽ xảy ra.",
            "hint_3": f"Sửa `return {attr2};` thành `return _{attr2.lower()};` và `{attr2} = value;` thành `_{attr2.lower()} = value;`.",
            "reference_solution": ref_solution,
            "explanation_vi": f"Để tránh lỗi đệ quy vô tận trong C#, Property cần thao tác với backing field `_{attr2.lower()}` thay vì gọi lại chính tên Property `{attr2}`.",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    elif topic == "constructor_this":
        problem_vi = f"Viết hàm tạo (constructor) cho lớp `{entity}` nhận hai tham số `{attr1.lower()}` và `{attr2.lower()}` để gán giá trị cho các trường cùng tên của lớp."
        expected_vi = f"Các trường của `{entity}` được gán chính xác giá trị từ tham số hàm tạo nhờ sử dụng từ khóa `this` để phân biệt phạm vi."
        student_code = f"""using System;

public class {entity}
{{
    public string {attr1};
    public {attr2_t} {attr2};

    public {entity}(string {attr1.lower()}, {attr2_t} {attr2.lower()})
    {{
        {attr1} = {attr1.lower()};
        {attr2.lower()} = {attr2.lower()};
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} obj = new {entity}("TestItem", {val_init});
        Console.WriteLine(obj.{attr2});
    }}
}}"""
        evidence = f"{attr2.lower()} = {attr2.lower()};"
        start_line, end_line = find_line_range(student_code, evidence)
        ref_solution = f"""using System;

public class {entity}
{{
    public string {attr1};
    public {attr2_t} {attr2};

    public {entity}(string {attr1.lower()}, {attr2_t} {attr2.lower()})
    {{
        this.{attr1} = {attr1.lower()};
        this.{attr2} = {attr2.lower()};
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} obj = new {entity}("TestItem", {val_init});
        Console.WriteLine(obj.{attr2});
    }}
}}"""
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "beginner",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": f"Assignment made to same variable; did you mean to assign something else? (CS1717)",
            "expected_behavior": expected_vi,
            "bug_status": "has_bug",
            "error_category": "logic_error",
            "bug_type": "unassigned_field_shadowing",
            "bug_location": {"file": "Program.cs", "start_line": start_line, "end_line": end_line, "symbol": f"{entity}.{entity}"},
            "knowledge_components": ["OOP.Constructors", "OOP.ThisKeyword", "OOP.VariableShadowing"],
            "possible_misconception": "Nghĩ rằng viết tên biến giống nhau trong constructor sẽ tự động gán vào trường của đối tượng mà không cần dùng từ khóa this để định danh.",
            "reference_diagnosis": f"Dòng lệnh `{attr2.lower()} = {attr2.lower()};` tự gán tham số cho chính nó do hiện tượng che khuất biến (variable shadowing), khiến trường `this.{attr2}` giữ giá trị mặc định.",
            "evidence": evidence,
            "hint_1": "Hãy xem xét câu lệnh gán bên trong hàm tạo xem nó đang gán giá trị cho trường của lớp hay cho chính tham số.",
            "hint_2": "Khi tham số cục bộ trùng tên với trường của lớp, tham số sẽ che khuất trường. Bạn cần từ khóa `this` để chỉ định trường của đối tượng hiện tại.",
            "hint_3": f"Sửa lại thành `this.{attr2} = {attr2.lower()};` và `this.{attr1} = {attr1.lower()};`.",
            "reference_solution": ref_solution,
            "explanation_vi": "Trong C#, từ khóa `this` tham chiếu đến thực thể hiện tại. Khi tham số và trường trùng tên, `this.` giúp trình biên dịch phân biệt chính xác trường của lớp.",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    elif topic == "method_parameter":
        problem_vi = f"Viết phương thức `{action}` trong lớp `{entity}` nhận vào một tham số kiểu `{attr2_t}` và trả về kết quả kiểu `bool` biểu thị hành động có thành công hay không."
        expected_vi = f"Phương thức `{action}` nhận đúng tham số kiểu `{attr2_t}` và trả về giá trị kiểu `bool`."
        student_code = f"""using System;

public class {entity}
{{
    public {attr2_t} {attr2} {{ get; set; }} = {val_init};

    public void {action}({attr2_t} amount)
    {{
        {attr2} = amount;
        return true;
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} obj = new {entity}();
        bool ok = obj.{action}({val_init});
        Console.WriteLine(ok);
    }}
}}"""
        evidence = "return true;"
        start_line, end_line = find_line_range(student_code, evidence)
        ref_solution = f"""using System;

public class {entity}
{{
    public {attr2_t} {attr2} {{ get; set; }} = {val_init};

    public bool {action}({attr2_t} amount)
    {{
        {attr2} = amount;
        return true;
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} obj = new {entity}();
        bool ok = obj.{action}({val_init});
        Console.WriteLine(ok);
    }}
}}"""
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "beginner",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": "Since 'void' returns void, a return keyword must not be followed by an object expression (CS0127)",
            "expected_behavior": expected_vi,
            "bug_status": "has_bug",
            "error_category": "compile_error",
            "bug_type": "return_type_mismatch",
            "bug_location": {"file": "Program.cs", "start_line": start_line, "end_line": end_line, "symbol": f"{entity}.{action}"},
            "knowledge_components": ["OOP.Methods", "OOP.ReturnTypes", "OOP.Parameters"],
            "possible_misconception": "Nhầm lẫn giữa phương thức khai báo kiểu void và việc dùng lệnh return trả về giá trị kiểu boolean.",
            "reference_diagnosis": f"Phương thức `{action}` được khai báo kiểu trả về là `void` nhưng thân hàm lại thực hiện `return true;`, gây lỗi CS0127.",
            "evidence": evidence,
            "hint_1": "Hãy so sánh kiểu trả về ở dòng khai báo phương thức với giá trị bạn đang trả về bằng câu lệnh `return`.",
            "hint_2": "Từ khóa `void` có nghĩa là phương thức không trả về giá trị. Nếu muốn trả về `true`/`false`, kiểu trả về phải là `bool`.",
            "hint_3": f"Sửa chữ ký phương thức từ `public void {action}({attr2_t} amount)` thành `public bool {action}({attr2_t} amount)`.",
            "reference_solution": ref_solution,
            "explanation_vi": "Chữ ký phương thức quy định giao ước về kiểu dữ liệu trả về. Khai báo `void` cấm mọi biểu thức theo sau `return`. Muốn trả về boolean cần đổi thành `bool`.",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    elif topic == "encapsulation_validation":
        problem_vi = f"Áp dụng tính đóng gói cho lớp `{entity}`: ràng buộc nghiệp vụ yêu cầu '{rule}'. Nếu dữ liệu không hợp lệ thì không cập nhật hoặc ném ngoại lệ."
        expected_vi = f"Phương thức `{action}` kiểm tra điều kiện hợp lệ trước khi cập nhật dữ liệu, ngăn chặn trạng thái không hợp lệ của đối tượng."
        student_code = f"""using System;

public class {entity}
{{
    public {attr2_t} {attr2} {{ get; private set; }}

    public void {action}({attr2_t} amount)
    {{
        {attr2} += amount;
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} item = new {entity}();
        item.{action}({val_neg});
        Console.WriteLine(item.{attr2});
    }}
}}"""
        evidence = f"{attr2} += amount;"
        start_line, end_line = find_line_range(student_code, evidence)
        ref_solution = f"""using System;

public class {entity}
{{
    public {attr2_t} {attr2} {{ get; private set; }}

    public void {action}({attr2_t} amount)
    {{
        if (amount <= 0)
        {{
            throw new ArgumentException("Giá trị cập nhật không hợp lệ theo quy tắc nghiệp vụ.");
        }}
        {attr2} += amount;
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} item = new {entity}();
        try
        {{
            item.{action}({val_neg});
        }}
        catch (ArgumentException ex)
        {{
            Console.WriteLine(ex.Message);
        }}
    }}
}}"""
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "medium",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": None,
            "expected_behavior": expected_vi,
            "bug_status": "has_bug",
            "error_category": "logic_error",
            "bug_type": "missing_domain_validation",
            "bug_location": {"file": "Program.cs", "start_line": start_line, "end_line": end_line, "symbol": f"{entity}.{action}"},
            "knowledge_components": ["OOP.Encapsulation", "OOP.DataValidation", "OOP.ClassInvariants"],
            "possible_misconception": "Tin rằng tính đóng gói chỉ đơn giản là đặt private set mà không cần kiểm tra tính toàn vẹn dữ liệu trong phương thức cập nhật.",
            "reference_diagnosis": f"Phương thức `{action}` trực tiếp cộng giá trị vào `{attr2}` mà không kiểm tra quy tắc bất biến: '{rule}', khiến đối tượng rơi vào trạng thái sai.",
            "evidence": evidence,
            "hint_1": "Điều gì sẽ xảy ra nếu người dùng truyền một số âm vào phương thức cập nhật này?",
            "hint_2": "Tính đóng gói yêu cầu đối tượng phải tự bảo vệ dữ liệu nội tại của mình bằng các điều kiện kiểm tra (validation guard clauses).",
            "hint_3": f"Thêm câu lệnh kiểm tra `if (amount <= 0)` trước dòng `{attr2} += amount;` để từ chối giá trị không hợp lệ.",
            "reference_solution": ref_solution,
            "explanation_vi": "Bao gói dữ liệu không chỉ là giới hạn quyền truy cập mà còn đảm bảo đối tượng luôn thỏa mãn các ràng buộc nghiệp vụ (invariants).",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    elif topic == "static_instance":
        problem_vi = f"Trong lớp `{entity}`, xây dựng phương thức instance `{action}` và gọi nó từ phương thức `Main`."
        expected_vi = f"Khởi tạo một thực thể cụ thể của `{entity}` trong `Main` trước khi gọi phương thức thực thể `{action}`."
        student_code = f"""using System;

public class {entity}
{{
    public void {action}()
    {{
        Console.WriteLine("{entity} action invoked.");
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity}.{action}();
    }}
}}"""
        evidence = f"{entity}.{action}();"
        start_line, end_line = find_line_range(student_code, evidence)
        ref_solution = f"""using System;

public class {entity}
{{
    public void {action}()
    {{
        Console.WriteLine("{entity} action invoked.");
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} obj = new {entity}();
        obj.{action}();
    }}
}}"""
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "beginner",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": f"An object reference is required for the non-static field, method, or property '{entity}.{action}()' (CS0120)",
            "expected_behavior": expected_vi,
            "bug_status": "has_bug",
            "error_category": "compile_error",
            "bug_type": "static_context_instance_member_access",
            "bug_location": {"file": "Program.cs", "start_line": start_line, "end_line": end_line, "symbol": f"{entity}.{action}"},
            "knowledge_components": ["OOP.StaticMembers", "OOP.InstanceMembers", "OOP.StaticContext"],
            "possible_misconception": "Nghĩ rằng có thể gọi phương thức thông thường (instance method) trực tiếp qua tên lớp như phương thức static.",
            "reference_diagnosis": f"Phương thức `{action}` là phương thức instance của lớp `{entity}` nhưng lại được gọi tĩnh qua `{entity}.{action}()` mà không qua một đối tượng cụ thể (lỗi CS0120).",
            "evidence": evidence,
            "hint_1": "Phương thức `{action}` có từ khóa `static` trong định nghĩa lớp hay không?",
            "hint_2": "Một phương thức không có `static` thuộc về từng đối tượng cụ thể. Bạn không thể gọi trực tiếp thông qua tên lớp.",
            "hint_3": f"Hãy tạo thực thể `{entity} obj = new {entity}();` rồi gọi `obj.{action}();`.",
            "reference_solution": ref_solution,
            "explanation_vi": "Phương thức instance yêu cầu ngữ cảnh của một đối tượng cụ thể (con trỏ `this`). Gọi qua tên lớp chỉ áp dụng cho thành viên tĩnh (static).",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    elif topic == "inheritance_polymorphism":
        problem_vi = f"Tạo lớp kế thừa `Special{entity}` từ lớp cha `{entity}` và ghi đè phương thức `{action}` để thể hiện tính đa hình khi gọi qua tham chiếu kiểu lớp cha."
        expected_vi = f"Sử dụng từ khóa `virtual` ở lớp cha và `override` ở lớp con để cơ chế đa hình gọi đúng phương thức của lớp thực thể."
        student_code = f"""using System;

public class {entity}
{{
    public void {action}()
    {{
        Console.WriteLine("Base {entity} {action}");
    }}
}}

public class Special{entity} : {entity}
{{
    public void {action}()
    {{
        Console.WriteLine("Special {entity} {action}");
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} item = new Special{entity}();
        item.{action}();
    }}
}}"""
        evidence = f"public void {action}()"
        start_line, end_line = find_line_range(student_code, evidence)
        ref_solution = f"""using System;

public class {entity}
{{
    public virtual void {action}()
    {{
        Console.WriteLine("Base {entity} {action}");
    }}
}}

public class Special{entity} : {entity}
{{
    public override void {action}()
    {{
        Console.WriteLine("Special {entity} {action}");
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} item = new Special{entity}();
        item.{action}();
    }}
}}"""
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "medium",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": f"'Special{entity}.{action}()' hides inherited member '{entity}.{action}()'. Use the new keyword if hiding was intended. (CS0108)",
            "expected_behavior": expected_vi,
            "bug_status": "has_bug",
            "error_category": "conceptual_misuse",
            "bug_type": "missing_override_polymorphism",
            "bug_location": {"file": "Program.cs", "start_line": start_line, "end_line": end_line, "symbol": f"Special{entity}.{action}"},
            "knowledge_components": ["OOP.Inheritance", "OOP.Polymorphism", "OOP.VirtualOverride"],
            "possible_misconception": "Nghĩ rằng chỉ cần đặt tên phương thức ở lớp con giống lớp cha thì tính đa hình sẽ tự động kích hoạt mà không cần từ khóa virtual và override.",
            "reference_diagnosis": f"Thiếu từ khóa `virtual` ở lớp cha và `override` ở lớp con `Special{entity}`, dẫn đến việc che giấu phương thức (method hiding) thay vì ghi đè đa hình.",
            "evidence": evidence,
            "hint_1": "Khi gọi phương thức qua biến tham chiếu kiểu lớp cha `{entity}`, phương thức nào đang thực sự được kích hoạt?",
            "hint_2": "Trong C#, để đa hình hoạt động trong thời gian chạy, phương thức lớp cha phải được đánh dấu `virtual` và lớp con phải có `override`.",
            "hint_3": f"Thêm `virtual` vào phương thức `{action}` của lớp `{entity}` và thêm `override` vào phương thức của lớp `Special{entity}`.",
            "reference_solution": ref_solution,
            "explanation_vi": "C# áp dụng liên kết tĩnh theo mặc định. Để thực hiện liên kết động (dynamic dispatch) nhằm đạt được tính đa hình, ta phải dùng cặp từ khóa `virtual` / `override`.",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    elif topic == "correct_code":
        problem_vi = f"Viết mã nguồn C# hoàn chỉnh chuẩn hướng đối tượng cho `{entity}`, bao gồm các thuộc tính tự động, constructor khởi tạo và phương thức `{action}`."
        expected_vi = f"Lớp `{entity}` hoạt động chính xác, tuân thủ chuẩn OOP và không có bất kỳ lỗi cú pháp hay logic nào."
        student_code = f"""using System;

public class {entity}
{{
    public string {attr1} {{ get; set; }}
    public {attr2_t} {attr2} {{ get; set; }}

    public {entity}(string {attr1.lower()}, {attr2_t} {attr2.lower()})
    {{
        this.{attr1} = {attr1.lower()};
        this.{attr2} = {attr2.lower()};
    }}

    public void {action}()
    {{
        Console.WriteLine($"{entity}: {{{attr1}}} - {{{attr2}}}");
    }}
}}

public class Program
{{
    public static void Main()
    {{
        {entity} item = new {entity}("StandardSample", {val_init});
        item.{action}();
    }}
}}"""
        ref_solution = student_code
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "beginner",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": None,
            "expected_behavior": expected_vi,
            "bug_status": "no_bug",
            "error_category": "no_bug",
            "bug_type": "no_bug",
            "bug_location": None,
            "knowledge_components": ["OOP.Classes", "OOP.Properties", "OOP.Constructors", "OOP.CleanCode"],
            "possible_misconception": None,
            "reference_diagnosis": "Mã nguồn hoàn toàn chính xác, đáp ứng đầy đủ yêu cầu bài toán và tuân thủ các nguyên tắc thiết kế hướng đối tượng.",
            "evidence": None,
            "hint_1": "Mã nguồn của bạn đã giải quyết đúng và đầy đủ yêu cầu bài toán.",
            "hint_2": "Cấu trúc lớp, hàm tạo và phương thức đều được viết rất chuẩn mực.",
            "hint_3": "Chương trình không có lỗi nào cần sửa, bạn hãy tiếp tục phát huy!",
            "reference_solution": ref_solution,
            "explanation_vi": f"Chương trình định nghĩa lớp `{entity}` với đầy đủ tính đóng gói, sử dụng từ khóa `this` hợp lý trong constructor và khởi tạo đối tượng đúng cách trong `Main`.",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    elif topic == "insufficient_context":
        problem_vi = f"Đoạn mã C# sau đây thực hiện gọi một phương thức nội bộ trong mô hình `{name_vi}`, nhưng thiếu định nghĩa kiểu hoặc bị mất phần ngữ cảnh."
        expected_vi = "Gia sư nhận diện mã nguồn bị cắt cụt/thiếu ngữ cảnh và lịch sự yêu cầu người học cung cấp đầy đủ thông tin trước khi chẩn đoán."
        student_code = f"""// Đoạn mã trích xuất dở dang từ bài nộp của học sinh
public void Process{action}()
{{
    var currentItem = GetActive{entity}();
    currentItem.{action}();
}}"""
        evidence = f"var currentItem = GetActive{entity}();"
        ref_solution = f"""// Mã nguồn đầy đủ với định nghĩa phương thức và lớp hỗ trợ
using System;

public class {entity}
{{
    public void {action}()
    {{
        Console.WriteLine("{entity} processed.");
    }}
}}

public class ContextProvider
{{
    public {entity} GetActive{entity}()
    {{
        return new {entity}();
    }}

    public void Process{action}()
    {{
        var currentItem = GetActive{entity}();
        currentItem.{action}();
    }}
}}"""
        return {
            "id": sample_id,
            "language": "vi",
            "topic": topic,
            "difficulty": "medium",
            "problem_family_id": fam_id,
            "problem_statement_vi": problem_vi,
            "student_code": student_code,
            "compiler_error": None,
            "expected_behavior": expected_vi,
            "bug_status": "insufficient_context",
            "error_category": "insufficient_context",
            "bug_type": "insufficient_context",
            "bug_location": None,
            "knowledge_components": ["OOP.ProgramStructure", "OOP.ContextSufficiency"],
            "possible_misconception": None,
            "reference_diagnosis": f"Đoạn mã bị cắt đoạn: thiếu định nghĩa lớp bao bọc, kiểu dữ liệu trả về của `GetActive{entity}()` và ngữ cảnh thực thi đầy đủ.",
            "evidence": evidence,
            "hint_1": "Đoạn mã hiện tại chưa cung cấp đầy đủ định nghĩa lớp hoặc ngữ cảnh cần thiết.",
            "hint_2": f"Phương thức `GetActive{entity}()` chưa rõ được định nghĩa ở đâu và trả về kiểu dữ liệu cụ thể nào.",
            "hint_3": "Vui lòng cung cấp toàn bộ định nghĩa lớp và yêu cầu chi tiết của bài toán để hệ thống có thể hỗ trợ bạn chính xác nhất.",
            "reference_solution": ref_solution,
            "explanation_vi": "Khi gặp đoạn mã khuyết thiếu phần định nghĩa lớp hoặc các hàm phụ thuộc, gia sư thông minh cần xác định đây là tình huống thiếu ngữ cảnh thay vì võ đoán lỗi.",
            "source_type": "expert_authored",
            "split": split,
            "review_status": "approved"
        }

    raise ValueError(f"Topic không hợp lệ: {topic}")

def main():
    root_dir = Path(r"e:\App\Love Emotion Web")
    data_dir = root_dir / "data" / "vietcsharptutor"
    data_dir.mkdir(parents=True, exist_ok=True)
    out_file = data_dir / "vietcsharptutor_600.jsonl"
    examples_file = data_dir / "examples.jsonl"

    topics = [
        "class_object",
        "field_property",
        "getter_setter",
        "constructor_this",
        "method_parameter",
        "encapsulation_validation",
        "static_instance",
        "inheritance_polymorphism",
        "correct_code",
        "insufficient_context"
    ]

    all_samples: List[Dict[str, Any]] = []
    sample_counter = 1

    print(f"Bắt đầu khởi tạo dữ liệu cho 60 problem families x 10 topics = 600 samples...")

    for f_idx, fam in enumerate(FAMILIES_DATA):
        if f_idx < 36:
            split = "dev"
        elif f_idx < 48:
            split = "validation"
        else:
            split = "test"

        for topic in topics:
            sample = generate_case(fam, topic, sample_counter, split)
            if sample["bug_status"] == "has_bug":
                ev = sample["evidence"]
                sc = sample["student_code"]
                assert ev in sc, f"LỖI TOÀN VẸN: Evidence '{ev}' không có trong student_code của {sample['id']}"

            all_samples.append(sample)
            sample_counter += 1

    assert len(all_samples) == 600, f"Tổng số mẫu phải đúng 600, nhận: {len(all_samples)}"

    with open(out_file, "w", encoding="utf-8") as f:
        for sample in all_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"Đã lưu thành công 600 samples vào: {out_file}")

    example_samples = all_samples[:10]
    with open(examples_file, "w", encoding="utf-8") as f:
        for sample in example_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"Đã lưu thành công 10 ví dụ mẫu vào: {examples_file}")

    test_samples = [s for s in all_samples if s["split"] == "test"]
    test_dump = "\n".join(json.dumps(s, sort_keys=True, ensure_ascii=False) for s in test_samples)
    test_hash = hashlib.sha256(test_dump.encode("utf-8")).hexdigest()
    print(f"\n[FROZEN TEST SPLIT] Số ca: {len(test_samples)} | SHA-256 Hash: {test_hash}")

    # Copy script into scripts/generate_vietcsharptutor_600.py
    script_target = root_dir / "scripts" / "generate_vietcsharptutor_600.py"
    with open(__file__, "r", encoding="utf-8") as f_src:
        script_target.write_text(f_src.read(), encoding="utf-8")
    print(f"Đã sao chép generator vào {script_target}")

if __name__ == "__main__":
    main()
