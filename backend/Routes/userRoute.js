// importing router from express
import { Router } from "express";
import multer from "multer";

// importing controller functions
import {
  createNewUser,
  deleteUser,
  getAllUser,
  getOneUser,
  resetPassword,
  updateUser,
} from "../Controller/userController.js";

// create router application for taking and providing req and res
const router = Router();
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// router queries
router.get("/getusers", getAllUser);
router.get("/getuser/:email", getOneUser);
router.post("/signup", upload.single("image"), createNewUser);
router.patch("/update/:id", updateUser);
router.patch("/resetpasswd", resetPassword);
router.delete("/delete/:email", deleteUser);
// router.get("/verify" ,  d)

// exporting router application
export default router;
