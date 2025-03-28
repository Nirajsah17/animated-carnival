// /src/routes/userRoutes.js
import express from "express";
import UserController from "../controller/userController.js";

const router = express.Router();

// User routes
router.post("/", UserController.createUser);
router.get("/", UserController.getAllUsers);
router.get("/:id", UserController.getUserById);

export default router;
